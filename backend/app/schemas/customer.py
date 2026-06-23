# app/schemas/customer.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CustomerBase(BaseModel):
    full_name: str = Field(..., example="Jane Doe")
    email: EmailStr | None = Field(None, example="jane@example.com")
    phone_number: str | None = Field(None, example="+254712345678")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    is_active: bool | None = None

class CustomerResponse(CustomerBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True