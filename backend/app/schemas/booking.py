# app/schemas/booking.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceItem(BaseModel):
    service_id: int = Field(..., examples=[2])


class BookingBase(BaseModel):
    customer_id: int = Field(..., examples=[1])
    services: List[ServiceItem] = Field(..., description="List of service ids included in this booking")
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
    # Return list of booked service ids for convenience
    service_ids: List[int] = []

    class Config:
        from_attributes = True

class BookingOut(BookingInDBBase):
    pass