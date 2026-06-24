# app/schemas/booking.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class BookingBase(BaseModel):
    customer_id: int
    service_id: int
    stylist_id: int | None = None
    start_time: datetime = Field(..., example="2026-07-01T10:00:00+03:00")
    notes: str | None = Field(None, example="Prefers a skin fade and low trim on top")

class BookingCreate(BookingBase):
    # We will compute the end_time dynamically in the route logic 
    # based on the duration of the service chosen!
    pass

class BookingUpdate(BaseModel):
    stylist_id: int | None = None
    start_time: datetime | None = None
    status: str | None = Field(None, example="cancelled") # pending, confirmed, cancelled, completed
    notes: str | None = None

class BookingResponse(BookingBase):
    id: int
    tenant_id: int
    end_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True