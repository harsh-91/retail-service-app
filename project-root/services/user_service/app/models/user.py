from pydantic import BaseModel, EmailStr, constr, Field, field_validator
from typing import Optional, List

class UserCreate(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    username: constr(strip_whitespace=True, min_length=3, max_length=30)
    mobile: constr(strip_whitespace=True, min_length=10, max_length=15)
    business_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    password: constr(min_length=8, max_length=128)
    email: Optional[EmailStr] = None
    full_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    language_pref: str = Field("en", description="Language preference")
    device_model: Optional[constr(strip_whitespace=True, max_length=100)] = None
    device_type: Optional[constr(strip_whitespace=True, max_length=50)] = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @field_validator("language_pref")
    @classmethod
    def valid_language(cls, v):
        allowed = {"en", "hi", "bn", "te", "ta"}
        if v not in allowed:
            raise ValueError("Not a supported language")
        return v
    
class UserLogin(BaseModel):
    tenant_id: str = ...  # Required!
    username: Optional[str] = None
    mobile: Optional[str] = None
    password: str

class UserProfile(BaseModel):
    tenant_id: str
    username: str
    mobile: str
    business_name: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    language_pref: str
    device_model: Optional[str] = None
    device_type: Optional[str] = None
    roles: List[str]  # ["owner", "admin", "employee"], etc.

class UserProfileUpdate(BaseModel):
    full_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    language_pref: Optional[str] = None
    device_model: Optional[str] = None
    device_type: Optional[str] = None
