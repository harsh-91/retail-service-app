from pydantic import BaseModel, Field
from typing import Optional

class ItemCreate(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier for data isolation")
    item_id: str = Field(..., description="Unique ID or SKU")
    item_name: str
    quantity: int = Field(ge=0)
    min_quantity: int = Field(ge=0)
    description: Optional[str] = None

class ItemUpdate(BaseModel):
    tenant_id: Optional[str] = Field(None, description="Tenant identifier for data isolation")
    item_name: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class StockAdjust(BaseModel):
    tenant_id: str = Field(..., description="Tenant identifier for data isolation")
    delta: int  # Positive (restock) or negative (sale/adjustment)

class ItemOut(BaseModel):
    tenant_id: str
    item_id: str
    item_name: str
    quantity: int
    min_quantity: int
    description: Optional[str] = None
    last_updated: Optional[str] = None
