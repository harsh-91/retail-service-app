from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, Request
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal, Dict
from datetime import datetime, date
from uuid import uuid4

# Dependency/mock imports for this example
from core.auth_utils import get_current_user, get_current_tenant
from db.sale_db import (
    add_sale, get_sale, mark_udhaar_paid, get_sales_summary,
    get_customer_udhaar_total, get_customer_credit_limit, set_customer_credit_limit,
    set_pending_inventory_deduction, deduct_inventory, inventory_exists, get_available_stock
)
from utils.localization import get_message
from utils.subscription import tenant_is_premium
from utils.export_utils import export_sales_csv, export_sales_pdf
from utils.payment import create_upi_payment, handle_payment_webhook
from utils.notifications import send_invoice_whatsapp

router = APIRouter()

# --- Models ---

class SaleCreate(BaseModel):
    tenant_id: str
    establishment_id: str
    item_id: str
    item_name: str
    quantity: int = Field(..., gt=0)
    price_per_unit: float
    payment_method: Literal["CASH", "UPI", "CREDIT"]
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    user: str

class SaleOut(BaseModel):
    tenant_id: str
    establishment_id: str
    sale_id: str
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    total_price: float
    payment_method: str
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    udhaar_paid: Optional[bool] = False
    udhaar_paid_on: Optional[datetime] = None
    amount_received: Optional[float] = None
    user: str
    timestamp: datetime
    low_stock_warn: Optional[bool] = None
    stock_pending_deduction: Optional[bool] = None
    gst_invoice: Optional[dict] = None

class SalePaymentUpdate(BaseModel):
    tenant_id: str
    sale_id: str
    amount_received: float
    payment_method: Literal["CASH", "UPI"]
    received_on: datetime

# --- Helpers ---

def check_localized(request: Request, key: str, **kwargs):
    lang = request.headers.get("Accept-Language", "en")
    return get_message(key, lang, **kwargs)

# --- Endpoints ---

# Record a sale (supports credit, live stock deduction/warning)
@router.post("/sales", response_model=SaleOut)
def create_sale(sale: SaleCreate, request: Request,
                user=Depends(get_current_user),
                tenant=Depends(get_current_tenant)):
    # 1. Credit check if udhaar
    if sale.is_udhaar:
        udhaar_total = get_customer_udhaar_total(sale.tenant_id, sale.establishment_id, sale.customer_id)
        limit = get_customer_credit_limit(sale.tenant_id, sale.establishment_id, sale.customer_id)
        if udhaar_total + (sale.quantity * sale.price_per_unit) > limit:
            raise HTTPException(400, check_localized(request, "udhaar_limit_breach"))
    # 2. Stock management
    stock_exists = inventory_exists(sale.tenant_id, sale.establishment_id, sale.item_id, sale.user)
    stock_status_msg = None
    low_warn = False
    pending_stock = False
    if stock_exists:
        available = get_available_stock(sale.tenant_id, sale.establishment_id, sale.item_id, sale.user)
        if available >= sale.quantity:
            deduct_inventory(sale.tenant_id, sale.establishment_id, sale.item_id, sale.quantity, sale.user)
            if available - sale.quantity <= 2:
                stock_status_msg = check_localized(request, "low_stock_warn", item=sale.item_name)
                low_warn = True
        else:
            stock_status_msg = check_localized(request, "insufficient_stock", item=sale.item_name)
            pending_stock = True
            set_pending_inventory_deduction(sale.tenant_id, sale.establishment_id, sale.item_id, sale.quantity, sale.user)
    else:
        # Allow sale, mark as pending inventory deduction
        pending_stock = True
        set_pending_inventory_deduction(sale.tenant_id, sale.establishment_id, sale.item_id, sale.quantity, sale.user)
        stock_status_msg = check_localized(request, "item_not_in_inventory", item=sale.item_name)
    # 3. Save sale record
    sale_data = sale.dict()
    sale_data["sale_id"] = str(uuid4())
    sale_data["total_price"] = sale.quantity * sale.price_per_unit
    sale_data["timestamp"] = datetime.utcnow()
    sale_data["low_stock_warn"] = low_warn
    sale_data["stock_pending_deduction"] = pending_stock
    out = add_sale(sale_data)
    if stock_status_msg:
        out["warning"] = stock_status_msg
    return out

# Mark udhaar as paid (credit repayment)
@router.patch("/sales/{sale_id}/receive_payment", response_model=SaleOut)
def receive_udhaar_payment(sale_id: str, update: SalePaymentUpdate, request: Request,
                           user=Depends(get_current_user), tenant=Depends(get_current_tenant)):
    updated = mark_udhaar_paid(
        tenant_id=update.tenant_id,
        sale_id=sale_id,
        amount_received=update.amount_received,
        payment_method=update.payment_method
    )
    if not updated:
        raise HTTPException(404, check_localized(request, "udhaar_not_found"))
    return get_sales(update.tenant_id, sale_id=sale_id)[0]

# Get all sales and filter by date or user
@router.get("/sales", response_model=List[SaleOut])
def list_sales(tenant_id: str, establishment_id: Optional[str] = None, from_date: Optional[date] = None,
               to_date: Optional[date] = None, user: Optional[str] = None, request: Request = None):
    sales = get_sales(tenant_id, establishment_id, from_date, to_date, user)
    return sales

# Set customer credit/udhaar limit
@router.patch("/sales/customers/{customer_id}/set_udhaar_limit")
def set_udhaar_limit_api(tenant_id: str, establishment_id: str, customer_id: str, limit: float, user=Depends(get_current_user)):
    return set_customer_credit_limit(tenant_id, establishment_id, customer_id, limit, user)

# UPI payment: Start payment, and webhook for confirmation
@router.post("/sales/{sale_id}/start_upi")
def start_upi_payment(sale_id: str, request: Request):
    upi_payload = create_upi_payment(sale_id)
    return {"upi_uri": upi_payload["uri"], "qr": upi_payload.get("qr")}

@router.post("/sales/payment_webhook")
def payment_webhook(payload: dict):
    return handle_payment_webhook(payload)

# Sales summaries
@router.get("/sales/summary/daily")
def sales_summary_daily(tenant_id: str, date: date, establishment_id: Optional[str] = None):
    return get_sales_summary(tenant_id, "daily", date, establishment_id)

@router.get("/sales/summary/weekly")
def sales_summary_weekly(tenant_id: str, week_start: date, establishment_id: Optional[str] = None):
    return get_sales_summary(tenant_id, "weekly", week_start, establishment_id)

# Export sales as CSV/PDF (Premium only)
@router.get("/sales/export")
def export_sales(tenant_id: str, filetype: Literal["csv", "pdf"] = "csv", user=Depends(get_current_user)):
    if not tenant_is_premium(tenant_id):
        raise HTTPException(403, "Feature available to premium subscribers only")
    if filetype == "csv":
        return export_sales_csv(tenant_id)
    return export_sales_pdf(tenant_id)

# GST invoice (Premium only)
@router.post("/sales/{sale_id}/gst_invoice")
def generate_gst_invoice(sale_id: str, tenant_id: str):
    if not tenant_is_premium(tenant_id):
        raise HTTPException(403, "GST Billing only available to premium subscribers")
    # Logic to create/generate PDF invoice...
    # ...return invoice URL or binary as per your setup
    return {"status": "pending", "info": "GST invoice generation stub"}

# WhatsApp export/share (file/link generation + send)
@router.post("/sales/{sale_id}/share_invoice")
def share_invoice_whatsapp(sale_id: str, tenant_id: str):
    # Lookup invoice/download link, call WhatsApp send utility
    url = export_sales_pdf(tenant_id, sale_id)
    res = send_invoice_whatsapp(sale_id, url)
    return {"result": res}

# Localized health endpoint (sample for testing)
@router.get("/health")
def health(request: Request):
    return {"status": check_localized(request, "healthy")}

