# app/models/customer.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.connection import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Backwards-compatible aliases expected by tests / older code
    @property
    def name(self) -> str:
        return self.full_name

    @name.setter
    def name(self, value: str) -> None:
        self.full_name = value

    @property
    def phone(self) -> str | None:
        return self.phone_number

    @phone.setter
    def phone(self, value: str | None) -> None:
        self.phone_number = value