from fastapi import APIRouter, HTTPException
from models.tenants import TenantCreate
from app.db.tenant_db import add_tenant, get_tenant

router = APIRouter()

@router.post("/tenants")
def create_tenant(data: TenantCreate):
    if get_tenant(data.tenant_id):
        raise HTTPException(status_code=409, detail="Tenant ID already exists")
    add_tenant(data)
    return {"msg": "Tenant created"}

@router.get("/tenants/{tenant_id}")
def read_tenant(tenant_id: str):
    tenant = get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
