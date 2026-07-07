# app/models/booking_service.py
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base


class BookingService(Base):
    __tablename__ = "booking_services"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)

    # Snapshot of the service price at time of booking (avoid historical drift)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="services")
