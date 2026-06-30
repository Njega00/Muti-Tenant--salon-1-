# app/crud/crud_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.service import Service  # Assumes your model is named Service
from app.schemas.service import ServiceCreate, ServiceUpdate

class CRUDService:
    def get_by_id(self, db: Session, *, tenant_id: int, service_id: int) -> Optional[Service]:
        return db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == tenant_id
        ).first()

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Service]:
        return db.query(Service).filter(
            Service.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def create_with_tenant(
        self, db: Session, *, obj_in: ServiceCreate, tenant_id: int
    ) -> Service:
        db_obj = Service(
            **obj_in.model_dump(),
            tenant_id=tenant_id,
            is_available=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Service, obj_in: ServiceUpdate
    ) -> Service:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

service_crud = CRUDService()