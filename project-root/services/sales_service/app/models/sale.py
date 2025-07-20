from pydantic import BaseModel, conint, constr, field_validator
from typing import Optional, List, Literal, Dict
from datetime import datetime

class GSTParty(BaseModel):
    name: str
    gstin: str
    address: str

class GSTInvoiceItem(BaseModel):
    item_id: str
    name: str
    qty: int
    rate: float
    value: float
    gst_rate: float
    gst_value: float

class GSTInvoice(BaseModel):
    invoice_number: str
    date: str
    supplier: GSTParty
    customer: GSTParty
    items: List[GSTInvoiceItem]
    total: float
    gst_total: float

class SaleCreate(BaseModel):
    tenant_id: str
    item_id: str
    item_name: str
    quantity: conint(gt=0)
    price_per_unit: float
    payment_method: Literal["CASH", "UPI", "CREDIT"]
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    user: str

    @field_validator("payment_method")
    @classmethod
    def valid_payment(cls, v):
        allowed = {"CASH", "UPI", "CREDIT"}
        if v.upper() not in allowed:
            raise ValueError("Invalid payment method")
        return v.upper()

class SaleOut(BaseModel):
    tenant_id: str
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
    gst_invoice: Optional[GSTInvoice] = None
    invoice_pdf_url: Optional[str] = None

class SaleGSTInvoiceCreate(BaseModel):
    tenant_id: str
    establishment_id: Optional[str] = None
    sale_id: str
    supplier: GSTParty
    customer: GSTParty
    # potentially override item/rate/qty if you want

class SaleInvoiceShareRequest(BaseModel):
    tenant_id: str
    sale_id: str
    whatsapp: str  # recipient phone
