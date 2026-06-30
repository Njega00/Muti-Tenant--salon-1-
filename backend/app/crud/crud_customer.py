# app/crud/crud_customer.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CRUDCustomer:
    def get_by_id(self, db: Session, *, tenant_id: int, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(
            Customer.id == customer_id, 
            Customer.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Customer]:
        return db.query(Customer).filter(
            Customer.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: CustomerCreate, tenant_id: int
    ) -> Customer:
        db_obj = Customer(
            **obj_in.model_dump(),
            tenant_id=tenant_id,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Customer, obj_in: CustomerUpdate
    ) -> Customer:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Customer:
        obj = db.query(Customer).get(id)
        db.delete(obj)
        db.commit()
        return obj

customer_crud = CRUDCustomer()