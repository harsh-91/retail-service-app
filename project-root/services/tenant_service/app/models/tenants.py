from pydantic import BaseModel
from typing import Optional, Dict

class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    owner: str
    contact_info: Optional[Dict[str, str]] = None
    settings: Optional[Dict[str, str]] = None
