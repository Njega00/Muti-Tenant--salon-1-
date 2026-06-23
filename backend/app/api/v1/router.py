# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, services  # <-- Import services

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(services.router, prefix="/services", tags=["Salon Services"])  # <-- Mount services