# app/api/v1/endpoints/customers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.core.deps import get_current_user, CurrentUser
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Register a new customer locked under the active tenant directory."""
    new_customer = Customer(
        tenant_id=current_user.tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Fetch all clients belonging exclusively to this workspace."""
    return db.query(Customer).filter(Customer.tenant_id == current_user.tenant_id).all()


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Modify a customer profile, protecting against cross-tenant tampering."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.tenant_id == current_user.tenant_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer profiles not found in this workspace")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer