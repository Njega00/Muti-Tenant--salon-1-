# app/api/v1/endpoints/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import timedelta
from typing import List

from app.db.connection import get_db
from app.core.deps import get_current_user, CurrentUser
from app.models.booking import Booking
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Schedules an appointment, dynamically calculating runtimes and checking for overlaps."""
    # 1. Fetch service info to extract duration footprint
    service = db.query(Service).filter(
        Service.id == payload.service_id,
        Service.tenant_id == current_user.tenant_id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Selected service does not exist in this workspace.")

    # 2. Compute dynamic runtime block boundary
    calculated_end = payload.start_time + timedelta(minutes=service.duration_minutes)

    # 3. Double-Booking Guard: Check if the stylist has an active overlap
    if payload.stylist_id:
        overlapping_appointment = db.query(Booking).filter(
            Booking.tenant_id == current_user.tenant_id,
            Booking.stylist_id == payload.stylist_id,
            Booking.status == "confirmed",
            # Standard calendar intersection check formula:
            # (RequestedStart < ExistingEnd) AND (RequestedEnd > ExistingStart)
            and_(
                payload.start_time < Booking.end_time,
                calculated_end > Booking.start_time
            )
        ).first()

        if overlapping_appointment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The requested stylist is already booked during this time frame."
            )

    # 4. Instantiate and commit appointment block
    new_booking = Booking(
        tenant_id=current_user.tenant_id,
        customer_id=payload.customer_id,
        service_id=payload.service_id,
        stylist_id=payload.stylist_id,
        start_time=payload.start_time,
        end_time=calculated_end,
        notes=payload.notes
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve the isolated calendar timeline for the active tenant salon workspace."""
    return db.query(Booking).filter(Booking.tenant_id == current_user.tenant_id).all()