from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional, List

# --- Creation model: For new user registration ---
class UserCreate(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=30)
    mobile: constr(strip_whitespace=True, min_length=10, max_length=15)  # required
    Business_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    password: constr(min_length=8, max_length=128)
    email: Optional[EmailStr] = None  # optional
    full_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    language_pref: str = "en"
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

# --- For login: Accept username or mobile ---
class UserLogin(BaseModel):
    username: Optional[str] = None
    mobile: Optional[str] = None
    password: str

# --- User profile response model ---  
class UserProfile(BaseModel):
    username: str
    mobile: str
    Business_name: str
    email: Optional[str]
    full_name: Optional[str] = None
    language_pref: str
    device_model: Optional[str] = None
    device_type: Optional[str] = None
    roles: List[str]

# --- For updating user profile ---
class UserProfileUpdate(BaseModel):
    full_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    language_pref: Optional[str] = None
