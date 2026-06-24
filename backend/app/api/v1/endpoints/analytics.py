# app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.connection import get_db
from app.core.deps import get_current_user, CurrentUser
from app.models.booking import Booking
from app.models.service import Service
from app.schemas.analytics import TenantAnalyticsResponse, ServiceRevenueBreakdown

router = APIRouter()

@router.get("/dashboard", response_model=TenantAnalyticsResponse)
def get_tenant_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Generate high-level operational and financial insights for the active tenant workspace."""
    tenant_id = current_user.tenant_id

    # 1. Fetch categorical appointment counters
    status_counts = db.query(
        Booking.status, 
        func.count(Booking.id)
    ).filter(Booking.tenant_id == tenant_id).group_by(Booking.status).all()

    # Turn the list of tuples into a clean dict lookup table
    stats_map = {status: count for status, count in status_counts}
    
    total_bookings = sum(stats_map.values())
    active_bookings = stats_map.get("confirmed", 0)
    cancelled_bookings = stats_map.get("cancelled", 0)
    completed_bookings = stats_map.get("completed", 0)

    # 2. Compute Total Financial Yield (Only from Confirmed or Completed sessions)
    revenue_query = db.query(func.sum(Service.price)).join(
        Booking, Booking.service_id == Service.id
    ).filter(
        Booking.tenant_id == tenant_id,
        Booking.status.in_(["confirmed", "completed"])
    ).scalar()
    
    total_revenue = float(revenue_query) if revenue_query else 0.0

    # 3. Compile Popular Services Matrix
    services_performance = db.query(
        Service.name,
        func.count(Booking.id).label("bookings_count"),
        func.sum(Service.price).label("service_revenue")
    ).join(
        Booking, Booking.service_id == Service.id
    ).filter(
        Booking.tenant_id == tenant_id,
        Booking.status.in_(["confirmed", "completed"])
    ).group_by(Service.id).order_by(func.count(Booking.id).desc()).limit(5).all()

    popular_breakdown = [
        ServiceRevenueBreakdown(
            service_name=row[0],
            bookings_count=row[1],
            total_revenue=float(row[2]) if row[2] else 0.0
        )
        for row in services_performance
    ]

    return TenantAnalyticsResponse(
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        cancelled_bookings=cancelled_bookings,
        completed_bookings=completed_bookings,
        total_revenue=total_revenue,
        popular_services=popular_breakdown
    )