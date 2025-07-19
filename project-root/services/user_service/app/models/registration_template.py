from typing import List, Optional
from pydantic import BaseModel

class RegistrationField(BaseModel):
    name: str
    type: str
    label: str
    required: bool
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None

class RegistrationTemplate(BaseModel):
    template_id: str
    fields: List[RegistrationField]
    last_modified: Optional[str] = None
    created_by: Optional[str] = None
