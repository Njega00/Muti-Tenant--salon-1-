# app/schemas/customer.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Shared properties across creation and updates
class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    email: Optional[EmailStr] = Field(None, examples=["john@gmail.com"])
    phone_number: Optional[str] = Field(None, examples=["+254711111111"])
    notes: Optional[str] = None

# Properties received on Customer creation
class CustomerCreate(CustomerBase):
    pass

# Properties received on Customer update
class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

# Properties shared by models stored in DB
class CustomerInDBBase(CustomerBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to the client
class CustomerOut(CustomerInDBBase):
    pass