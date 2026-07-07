# app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.connection import get_db
from app.models.booking import Booking
from app.models.booking_service import BookingService
from app.models.customer import Customer
from app.models.service import Service
from app.models.tenant import Tenant
from app.schemas.analytics import TenantAnalyticsResponse, ServiceRevenueBreakdown

router = APIRouter()

def get_current_tenant(request: Request, db: Session = Depends(get_db)) -> Tenant:
    tenant_identifier = request.headers.get("X-Tenant-ID") or request.headers.get("host", "").split(".")[0]
    if not tenant_identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant context mapping identification metadata."
        )
    tenant = db.query(Tenant).filter(
        (Tenant.subdomain == tenant_identifier) | (Tenant.name == tenant_identifier)
    ).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested salon workspace partition not found."
        )
    return tenant


@router.get("/summary", response_model=TenantAnalyticsResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Fetch comprehensive business metrics and popular service catalog breakdowns
    scoped to the active tenant workspace partition.
    """
    # 1. Aggregate status metrics counts
    total_bookings = db.query(func.count(Booking.id)).filter(Booking.tenant_id == current_tenant.id).scalar() or 0
    active_count = db.query(func.count(Booking.id)).filter(Booking.tenant_id == current_tenant.id, Booking.status == "confirmed").scalar() or 0
    completed_count = db.query(func.count(Booking.id)).filter(Booking.tenant_id == current_tenant.id, Booking.status == "completed").scalar() or 0
    cancelled_count = db.query(func.count(Booking.id)).filter(Booking.tenant_id == current_tenant.id, Booking.status == "cancelled").scalar() or 0
    
    # 2. Total revenue from completed orders
    # Total revenue should sum the snapshot prices from booking_services for completed bookings
    total_revenue = db.query(func.sum(BookingService.price)).\
        join(Booking, BookingService.booking_id == Booking.id).\
        filter(Booking.tenant_id == current_tenant.id, Booking.status == "completed").\
        scalar() or 0.0

    # 3. Calculate popular service menu breakdowns
    popular_services_data = db.query(
        Service.name.label("service_name"),
        func.count(BookingService.id).label("bookings_count"),
        func.sum(BookingService.price).label("total_revenue")
    ).\
        join(BookingService, BookingService.service_id == Service.id).\
        join(Booking, BookingService.booking_id == Booking.id).\
        filter(Booking.tenant_id == current_tenant.id).\
        group_by(Service.id).\
        order_by(func.count(BookingService.id).desc()).\
        limit(5).\
        all()

    # Format the breakdowns to match ServiceRevenueBreakdown structure
    popular_services = [
        ServiceRevenueBreakdown(
            service_name=item.service_name,
            bookings_count=item.bookings_count,
            total_revenue=float(item.total_revenue or 0.0)
        ) for item in popular_services_data
    ]

    return {
        "total_bookings": total_bookings,
        "active_bookings": active_count,
        "cancelled_bookings": cancelled_count,
        "completed_bookings": completed_count,
        "total_revenue": float(total_revenue),
        "popular_services": popular_services
    }