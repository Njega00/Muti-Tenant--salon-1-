# app/schemas/booking.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    customer_id: int = Field(..., examples=[1])
    service_id: int = Field(..., examples=[2])
    user_id: Optional[int] = Field(None, description="Assigned staff/stylist ID", examples=[3])
    start_time: datetime = Field(..., examples=["2026-07-01T10:00:00"])
    notes: Optional[str] = Field(None, examples=["Prefers window seating if available"])

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    user_id: Optional[int] = None
    start_time: Optional[datetime] = None
    status: Optional[str] = Field(None, description="pending, confirmed, completed, cancelled")
    notes: Optional[str] = None

class BookingInDBBase(BookingBase):
    id: int
    tenant_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class BookingOut(BookingInDBBase):
    pass