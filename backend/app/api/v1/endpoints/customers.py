# app/api/v1/endpoints/customers.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.crud.crud_customer import customer_crud
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.models.tenant import Tenant

router = APIRouter()

# 🚀 INLINE TENANT DEPENDENCY MIDDLEWARE
def get_current_tenant(request: Request, db: Session = Depends(get_db)) -> Tenant:
    """
    Extracts the tenant dynamically via X-Tenant-ID header or the subdomain host header.
    """
    # 1. Look for a custom staging header, fallback to parsing subdomains (e.g., 'executive-kings.salon.com')
    tenant_identifier = request.headers.get("X-Tenant-ID") or request.headers.get("host", "").split(".")[0]
    
    if not tenant_identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant context mapping identification metadata."
        )
        
    # 2. Match the database tenant row criteria
    tenant = db.query(Tenant).filter(
        (Tenant.subdomain == tenant_identifier) | (Tenant.name == tenant_identifier)
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested salon workspace partition not found."
        )
    return tenant


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