# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, services, customers, bookings, analytics 

api_router = APIRouter()  # <--- Double check this exact naming!

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(services.router, prefix="/services", tags=["Salon Services"])
api_router.include_router(customers.router, prefix="/customers", tags=["Salon Customers"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Salon Bookings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Dashboard Analytics"])