from pydantic import BaseModel, condecimal, constr, field_validator
from typing import Optional, Literal
from datetime import datetime

# -- Payment creation (POST /payments) --
class PaymentCreate(BaseModel):
    tenant_id: str                           # Multi-tenancy enforcement
    sale_id: str                             # Which sale is this payment for
    user: str                                # Who is recording it
    amount: condecimal(gt=0)
    method: Literal["CASH", "UPI", "CREDIT"] # Only allowed business modes
    upi_vpa: Optional[str] = None            # Required for UPI, must validate below
    status: Literal["PENDING", "RECEIVED", "FAILED"] = "PENDING"
    created_at: Optional[datetime] = None    # Overridable for testing/backdating

    @field_validator('method')
    @classmethod
    def valid_method(cls, v):
        allowed = {"CASH", "UPI", "CREDIT"}
        if v not in allowed:
            raise ValueError(f"method must be one of {allowed}")
        return v

    @field_validator('upi_vpa')
    @classmethod
    def check_upi_for_upi(cls, v, values):
        if values.get("method") == "UPI" and not v:
            raise ValueError("upi_vpa is required for method UPI")
        return v

# -- Payment output (DB and GET /payments) --
class PaymentOut(BaseModel):
    tenant_id: str
    payment_id: str                          # Unique, generated in DB (_id as str)
    sale_id: str
    user: str
    amount: float
    method: str
    upi_vpa: Optional[str]
    status: Literal["PENDING", "RECEIVED", "FAILED"]
    created_at: datetime
    received_at: Optional[datetime] = None   # When marked as received
    note: Optional[str] = None               # For reconciliation/UPI ref/notes

# -- For marking a payment as received/failed
class PaymentStatusUpdate(BaseModel):
    tenant_id: str
    payment_id: str
    status: Literal["RECEIVED", "FAILED"]
    received_at: Optional[datetime] = None
    note: Optional[str] = None

# -- For analytics/reporting
class PaymentSummaryOut(BaseModel):
    tenant_id: str
    from_date: datetime
    to_date: datetime
    total_collections: float
    upi_count: int
    cash_count: int
    failed_count: int
    payments: Optional[list[PaymentOut]] = None
