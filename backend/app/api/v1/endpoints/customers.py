# app/api/v1/endpoints/customers.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_tenant  # Adjust path to your security deps
from app.crud.crud_customer import customer_crud
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.models.tenant import Tenant

router = APIRouter()

@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    *,
    db: Session = Depends(get_db),
    obj_in: CustomerCreate,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a new client profile under the active tenant space."""
    return customer_crud.create_with_tenant(db, obj_in=obj_in, tenant_id=current_tenant.id)


@router.get("/", response_model=List[CustomerOut])
def read_customers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve all clients matching the scoped tenant workspace partition."""
    return customer_crud.get_multi_by_tenant(
        db, tenant_id=current_tenant.id, skip=skip, limit=limit
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def read_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Fetch a single customer record ensuring it belongs exclusively to this tenant context."""
    customer = customer_crud.get_by_id(db, tenant_id=current_tenant.id, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer profile not found in this workspace context."
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer_profile(
    customer_id: int,
    obj_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update field properties on a target workspace customer file."""
    customer = customer_crud.get_by_id(db, tenant_id=current_tenant.id, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer target resource unavailable or completely invalid."
        )
    return customer_crud.update(db, db_obj=customer, obj_in=obj_in)