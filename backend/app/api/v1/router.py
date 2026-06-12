from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# As you build endpoints, register them here:
# from app.api.v1.endpoints import auth, staff, services, customers, bookings, products, checkout, dashboard
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
# api_router.include_router(services.router, prefix="/services", tags=["services"])
# api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
# api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
# api_router.include_router(products.router, prefix="/products", tags=["products"])
# api_router.include_router(checkout.router, prefix="/checkout", tags=["checkout"])
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
