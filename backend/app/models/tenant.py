from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    subdomain = Column(String, nullable=False, unique=True, index=True)
    business_type = Column(String, nullable=False, default="salon")
    timezone = Column(String, nullable=False, default="UTC")
    currency = Column(String, nullable=False, default="USD")
    plan = Column(String, nullable=False, default="trial")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    
    
