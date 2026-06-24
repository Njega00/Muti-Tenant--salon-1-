# app/schemas/analytics.py
from pydantic import BaseModel
from typing import List

class ServiceRevenueBreakdown(BaseModel):
    service_name: str
    bookings_count: int
    total_revenue: float

class TenantAnalyticsResponse(BaseModel):
    total_bookings: int
    active_bookings: int    # Confirmed status
    cancelled_bookings: int
    completed_bookings: int
    total_revenue: float
    popular_services: List[ServiceRevenueBreakdown]

    class Config:
        from_attributes = True