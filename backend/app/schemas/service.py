
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Fade Haircut & Wash"])
    description: Optional[str] = Field(None, examples=["Premium skin fade including hot towel wash"])
    price: Decimal = Field(..., ge=0.0, examples=[1500.00])  # Handles precise currency math
    duration_minutes: int = Field(..., ge=5, le=480, examples=[45])

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0.0)
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    is_available: Optional[bool] = None

class ServiceInDBBase(ServiceBase):
    id: int
    tenant_id: int
    is_available: bool

    class Config:
        from_attributes = True

class ServiceOut(ServiceInDBBase):
    pass