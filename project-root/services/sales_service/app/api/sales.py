from pydantic import BaseModel, conint, constr, field_validator
from typing import Optional, List, Literal
from datetime import datetime

# ---- Sale Creation (POST /sales) ----
class SaleCreate(BaseModel):
    tenant_id: str                            # Every sale must be linked to a business
    item_id: str                              # Links to Inventory item
    item_name: str
    quantity: conint(gt=0)                    # Must be positive
    price_per_unit: float
    payment_method: Literal["CASH", "UPI", "CREDIT"]
    customer_id: Optional[str] = None         # Needed for udhaar/credit tracking
    is_udhaar: bool = False
    user: str                                 # Username/login

    @field_validator("payment_method")
    @classmethod
    def valid_payment(cls, v):
        allowed = {"CASH", "UPI", "CREDIT"}
        if v.upper() not in allowed:
            raise ValueError("Invalid payment method")
        return v.upper()

# ---- Sale Output (GET /sales and similar) ----
class SaleOut(BaseModel):
    tenant_id: str
    sale_id: str                              # Auto-generated for each transaction
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    total_price: float
    payment_method: str
    customer_id: Optional[str] = None
    is_udhaar: bool = False
    udhaar_paid: Optional[bool] = False       # True if udhaar is cleared
    udhaar_paid_on: Optional[datetime] = None
    amount_received: Optional[float] = None
    user: str
    timestamp: datetime
    gst_invoice: Optional[dict] = None        # GST data (for B2B/freemium/exports)

# ---- Mark Udhaar as Paid (PATCH /sales/{id}/receive_payment) ----
class SalePaymentUpdate(BaseModel):
    tenant_id: str
    sale_id: str
    amount_received: float
    payment_method: Literal["CASH", "UPI"]
    received_on: datetime

    @field_validator("payment_method")
    @classmethod
    def valid_pay(cls, v):
        allowed = {"CASH", "UPI"}
        if v.upper() not in allowed:
            raise ValueError("Only CASH or UPI allowed for udhaar payment")
        return v.upper()

# ---- Daily/Weekly Summary Output ----
class SalesSummaryOut(BaseModel):
    tenant_id: str
    from_date: datetime
    to_date: datetime
    total_sales: float
    total_udhaar: float
    collections: float
    sales_count: int
    top_customers: Optional[List[str]] = None
    items_sold: Optional[List[dict]] = None   # [{'item_id':..., 'qty':...}, ...]
