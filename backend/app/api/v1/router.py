# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, services, customers  # <-- Import customers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(services.router, prefix="/services", tags=["Salon Services"])
api_router.include_router(customers.router, prefix="/customers", tags=["Salon Customers"])  # <-- Mount customers