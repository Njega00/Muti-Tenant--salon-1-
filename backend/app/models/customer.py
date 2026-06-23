from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True)  # Multi-tenant
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)