from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.payment import PaymentCreate, PaymentOut, PaymentStatusUpdate, PaymentSummaryOut
from app.db.payments_db import (
    create_payment,
    get_payment,
    list_payments,
    update_payment_status,
    payment_summary,
)
from app.core.upi_utils import generate_upi_qr
from app.core.auth_utils import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/payments", response_model=PaymentOut, status_code=201)
def initiate_payment(
    payment: PaymentCreate,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Query(..., description="Tenant ID"),
):
    # Ensure all payments are for the current tenant
    if payment.tenant_id != tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id mismatch")
    new_payment = create_payment(payment)
    # UPI mode: generate QR (business logic only; actual live integration elsewhere)
    if payment.method == "UPI":
        new_payment["upi_qr"] = generate_upi_qr(payment.upi_vpa, float(payment.amount))
    return PaymentOut(**new_payment)

@router.get("/payments", response_model=list[PaymentOut])
def get_all_payments(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Query(..., description="Tenant ID"),
    user: str = Query(None, description="Filter by user (optional)"),
):
    payments = list_payments(tenant_id=tenant_id, user=user or current_user["username"])
    return [PaymentOut(**p) for p in payments]

@router.get("/payments/{payment_id}", response_model=PaymentOut)
def get_payment_status(
    payment_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    current_user: dict = Depends(get_current_user),
):
    payment = get_payment(tenant_id, payment_id)
    if not payment or payment["user"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentOut(**payment)

@router.patch("/payments/{payment_id}/status", response_model=PaymentOut)
def update_status(
    payment_id: str,
    patch: PaymentStatusUpdate,
    tenant_id: str = Query(..., description="Tenant ID"),
    current_user: dict = Depends(get_current_user)
):
    if patch.tenant_id != tenant_id or patch.payment_id != payment_id:
        raise HTTPException(status_code=400, detail="tenant_id or payment_id mismatch")
    updated = update_payment_status(
        tenant_id=tenant_id,
        payment_id=payment_id,
        status=patch.status,
        received_at=patch.received_at,
        note=patch.note
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found or update failed")
    payment = get_payment(tenant_id, payment_id)
    return PaymentOut(**payment)

@router.get("/payments/summary", response_model=PaymentSummaryOut)
def get_payment_summary(
    tenant_id: str = Query(...),
    from_date: str = Query(..., description="YYYY-MM-DD"),
    to_date: str = Query(..., description="YYYY-MM-DD")
):
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    summary = payment_summary(tenant_id, from_dt, to_dt)
    return PaymentSummaryOut(**summary)
