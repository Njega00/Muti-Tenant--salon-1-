# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # 🚀 Make sure ForeignKey is imported!
from sqlalchemy.orm import relationship
from app.db.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # 🚀 FIX THIS LINE: Ensure ForeignKey point to "tenants.id" explicitly!
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="stylist") # owner, manager, stylist
    is_active = Column(Boolean, default=True)

    # Relationship back to the workspace tenant engine
    tenant = relationship("Tenant", back_populates="users")