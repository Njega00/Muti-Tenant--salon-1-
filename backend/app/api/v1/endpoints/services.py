# app/api/v1/endpoints/services.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.crud.crud_service import service_crud
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.models.tenant import Tenant

router = APIRouter()

# Reusing our rock-solid dynamic tenant resolution dependency
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


@router.post("/", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(
    *,
    db: Session = Depends(get_db),
    obj_in: ServiceCreate,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Add a new item to the salon's service menu catalog."""
    return service_crud.create_with_tenant(db, obj_in=obj_in, tenant_id=current_tenant.id)


@router.get("/", response_model=List[ServiceOut])
def read_services(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve all menu services belonging to this tenant workspace."""
    return service_crud.get_multi_by_tenant(
        db, tenant_id=current_tenant.id, skip=skip, limit=limit
    )


@router.get("/{service_id}", response_model=ServiceOut)
def read_service_by_id(
    service_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Fetch a specific service item after validating workspace tenant scope alignment."""
    service = service_crud.get_by_id(db, tenant_id=current_tenant.id, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service catalog item not found in this workspace context."
        )
    return service


@router.put("/{service_id}", response_model=ServiceOut)
def update_service_item(
    service_id: int,
    obj_in: ServiceUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Modify pricing, duration, or descriptions on a specific menu item."""
    service = service_crud.get_by_id(db, tenant_id=current_tenant.id, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target service item unavailable or invalid."
        )
    return service_crud.update(db, db_obj=service, obj_in=obj_in)