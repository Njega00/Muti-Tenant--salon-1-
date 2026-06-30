# app/api/v1/endpoints/bookings.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.crud.crud_booking import booking_crud
from app.schemas.booking import BookingCreate, BookingUpdate, BookingOut
from app.models.tenant import Tenant

router = APIRouter()

# Unified dynamic tenant dependency lookup
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


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    *,
    db: Session = Depends(get_db),
    obj_in: BookingCreate,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Schedule a new client booking reservation entry inside the active workspace."""
    return booking_crud.create_with_tenant(db, obj_in=obj_in, tenant_id=current_tenant.id)


@router.get("/", response_model=List[BookingOut])
def read_appointments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Fetch the calendar appointment timelines recorded for this workspace partition."""
    return booking_crud.get_multi_by_tenant(
        db, tenant_id=current_tenant.id, skip=skip, limit=limit
    )


@router.get("/{booking_id}", response_model=BookingOut)
def read_appointment_by_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve an individual appointment ledger sheet verifying workspace authorization scope."""
    booking = booking_crud.get_by_id(db, tenant_id=current_tenant.id, booking_id=booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment record entry not found in this workspace context."
        )
    return booking


@router.put("/{booking_id}", response_model=BookingOut)
def update_appointment_status(
    booking_id: int,
    obj_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Modify booking parameters or switch current reservation execution states (e.g., confirm, cancel)."""
    booking = booking_crud.get_by_id(db, tenant_id=current_tenant.id, booking_id=booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target calendar block resource unavailable or invalid."
        )
    return booking_crud.update(db, db_obj=booking, obj_in=obj_in)
