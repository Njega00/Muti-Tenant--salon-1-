# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class TenantSignUp(BaseModel):
    salon_name: str
    salon_slug: str
    owner_name: str
    owner_email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str  # Added to support your security.py layout
    token_type: str