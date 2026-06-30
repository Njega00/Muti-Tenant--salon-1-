# app/crud/crud_booking.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.booking import Booking  # Assumes your model is named Booking
from app.models.customer import Customer
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingUpdate
from fastapi import HTTPException, status

class CRUDBooking:
    def get_by_id(self, db: Session, *, tenant_id: int, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        return db.query(Booking).filter(
            Booking.tenant_id == tenant_id
        ).order_by(Booking.start_time.asc()).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: BookingCreate, tenant_id: int
    ) -> Booking:
        # 🔒 Multi-Tenant Cross Validation Check
        customer_exists = db.query(Customer).filter(Customer.id == obj_in.customer_id, Customer.tenant_id == tenant_id).first()
        service_exists = db.query(Service).filter(Service.id == obj_in.service_id, Service.tenant_id == tenant_id).first()
        
        if not customer_exists or not service_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid relational references. Customer or Service does not exist within your salon workspace."
            )

        db_obj = Booking(
            **obj_in.model_dump(),
            tenant_id=tenant_id,
            status="pending"  # Default fallback state
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Booking, obj_in: BookingUpdate
    ) -> Booking:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

booking_crud = CRUDBooking()