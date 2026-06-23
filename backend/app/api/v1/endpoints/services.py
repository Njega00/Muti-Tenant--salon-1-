# app/api/v1/endpoints/services.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.service import Service  # Assumes your model class is named Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter()

@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("owner", "manager"))
):
    """Create a new service explicitly tied to the authenticated tenant."""
    new_service = Service(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        duration_minutes=payload.duration_minutes
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/", response_model=List[ServiceResponse])
def list_services(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # Any staff can view
):
    """Retrieve all services belonging exclusively to this salon tenant."""
    # The filter ensures complete tenant isolation
    services = db.query(Service).filter(Service.tenant_id == current_user.tenant_id).all()
    return services


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("owner", "manager"))
):
    """Modify a service, verifying ownership before processing."""
    service = db.query(Service).filter(
        Service.id == service_id, 
        Service.tenant_id == current_user.tenant_id
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found in this salon workspace")

    # Update only fields provided in the payload
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("owner"))
):
    """Completely remove a service from the tenant catalog."""
    service = db.query(Service).filter(
        Service.id == service_id, 
        Service.tenant_id == current_user.tenant_id
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found in this salon workspace")

    db.delete(service)
    db.commit()
    return None