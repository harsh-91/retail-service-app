from fastapi import APIRouter, HTTPException, status, Query
from app.models.inventory import ItemCreate, ItemUpdate, ItemOut, StockAdjust
from app.db.inventory_db import (
    add_item,
    update_item,
    delete_item,
    get_all_items,
    get_item,
    adjust_stock,
    get_low_stock_items
)

router = APIRouter()

@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    # item.tenant_id must be set by the client
    if get_item(item.tenant_id, item.item_id):
        raise HTTPException(status_code=409, detail="Item with this ID already exists in this tenant")
    try:
        item_id = add_item(item)
        item_db = get_item(item.tenant_id, item_id)
        return ItemOut(**item_db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create item: {str(e)}")

@router.get("/items", response_model=list[ItemOut])
def list_items(tenant_id: str = Query(..., description="Tenant ID")):
    items = get_all_items(tenant_id)
    return [ItemOut(**i) for i in items]

@router.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: str, tenant_id: str = Query(..., description="Tenant ID")):
    item = get_item(tenant_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemOut(**item)

@router.put("/items/{item_id}", response_model=ItemOut)
def modify_item(
    item_id: str,
    item: ItemUpdate,
    tenant_id: str = Query(..., description="Tenant ID")
):
    if not get_item(tenant_id, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    update_item(tenant_id, item_id, item)
    item_db = get_item(tenant_id, item_id)
    return ItemOut(**item_db)

@router.patch("/items/{item_id}/stock", response_model=ItemOut)
def patch_item_stock(
    item_id: str,
    adjust: StockAdjust,
    tenant_id: str = Query(..., description="Tenant ID")
):
    item = get_item(tenant_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if tenant_id != adjust.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id mismatch")
    try:
        adjust_stock(tenant_id, item_id, adjust.delta)
    except ValueError as ve:
        raise HTTPException(status_code=409, detail=str(ve))
    updated = get_item(tenant_id, item_id)
    return ItemOut(**updated)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: str, tenant_id: str = Query(..., description="Tenant ID")):
    if not get_item(tenant_id, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    delete_item(tenant_id, item_id)
    return

@router.get("/items/alerts/low-stock", response_model=list[ItemOut])
def low_stock_alerts(tenant_id: str = Query(..., description="Tenant ID")):
    """Return all items for this tenant where quantity <= min_quantity."""
    items = get_low_stock_items(tenant_id)
    return [ItemOut(**i) for i in items]
