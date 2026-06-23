# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.user import TenantSignUp, Token

# Importing your exact security utilities
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_salon(payload: TenantSignUp, db: Session = Depends(get_db)):
    if db.query(Tenant).filter(Tenant.slug == payload.salon_slug).first():
        raise HTTPException(status_code=400, detail="Salon URL slug already taken.")
    if db.query(User).filter(User.email == payload.owner_email).first():
        raise HTTPException(status_code=400, detail="Email address already registered.")

    # 1. Create the Tenant
    new_tenant = Tenant(name=payload.salon_name, slug=payload.salon_slug)
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)

    # 2. Create the Owner Admin linked to that tenant
    new_user = User(
        tenant_id=new_tenant.id,
        email=payload.owner_email,
        hashed_password=hash_password(payload.password), # Uses your hash_password function
        full_name=payload.owner_name,
        role="owner"
    )
    db.add(new_user)
    db.commit()

    return {"status": "success", "message": f"Tenant '{payload.salon_name}' initialized successfully."}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens using your specific signature contracts (passing user.id)
    access_token = create_access_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id, role=user.role)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }