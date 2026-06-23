from pydantic import BaseModel, Field
from datetime import datetime

# Shared properties
class ServiceBase(BaseModel):
    name: str = Field(..., example="Fade Cut & Wash")
    description: str | None = Field(None, example="Premium clipper cut with a relaxing wash")
    price: float = Field(..., gt=0, example=1500.00)  # KES or local currency
    duration_minutes: int = Field(..., gt=0, le=480, example=45)

# Properties to receive on service creation
class ServiceCreate(ServiceBase):
    pass

# Properties to receive on service update
class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    duration_minutes: int | None = Field(None, gt=0)

# Properties returned from the API (Database representation)
class ServiceResponse(ServiceBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True