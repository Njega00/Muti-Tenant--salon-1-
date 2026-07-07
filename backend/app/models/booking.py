# app/models/booking.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

    # The stylist or barber handling the appointment
    stylist_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timing configurations
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # Status matrix: pending, confirmed, cancelled, completed
    status = Column(String, default="confirmed", nullable=False)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to booking-service association (supports multi-service bookings)
    services = relationship("BookingService", back_populates="booking", cascade="all, delete-orphan")

    @property
    def service_ids(self):
        return [bs.service_id for bs in self.services]