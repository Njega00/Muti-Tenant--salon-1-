# backend/tests/test_multiservice_bookings.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.service import Service
from app.models.booking import Booking
from app.models.booking_service import BookingService
from app.schemas.booking import BookingCreate, ServiceItem
from app.crud.crud_booking import booking_crud


@pytest.fixture
def test_tenant(db: Session) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(name="test_salon", subdomain="test")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def test_customer(db: Session, test_tenant: Tenant) -> Customer:
    """Create a test customer."""
    customer = Customer(
        tenant_id=test_tenant.id,
        name="John Doe",
        phone="555-1234",
        email="john@example.com"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def test_services(db: Session, test_tenant: Tenant):
    """Create multiple test services."""
    services = [
        Service(
            tenant_id=test_tenant.id,
            name="Haircut",
            price=30.00,
            duration_minutes=30
        ),
        Service(
            tenant_id=test_tenant.id,
            name="Hair Coloring",
            price=75.00,
            duration_minutes=60
        ),
        Service(
            tenant_id=test_tenant.id,
            name="Beard Trim",
            price=15.00,
            duration_minutes=15
        ),
    ]
    for service in services:
        db.add(service)
    db.commit()
    for service in services:
        db.refresh(service)
    return services


class TestMultiserviceBookings:
    """Test suite for multiservice appointment bookings."""

    def test_create_multiservice_booking(self, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test creating a booking with multiple services."""
        # Create a booking with 2 services
        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),  # Haircut
                ServiceItem(service_id=test_services[1].id),  # Hair Coloring
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Customer wants full styling"
        )

        booking = booking_crud.create_with_tenant(
            db, obj_in=booking_create, tenant_id=test_tenant.id
        )

        assert booking.id is not None
        assert booking.status == "pending"
        assert booking.customer_id == test_customer.id
        assert len(booking.services) == 2

        # Verify BookingService associations
        booking_services = db.query(BookingService).filter(
            BookingService.booking_id == booking.id
        ).all()
        assert len(booking_services) == 2

        # Verify prices were snapshotted
        prices = sorted([bs.price for bs in booking_services])
        assert prices == [30.00, 75.00]

    def test_create_single_service_booking(self, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test creating a booking with a single service (backward compatibility)."""
        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),  # Haircut
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Just a haircut"
        )

        booking = booking_crud.create_with_tenant(
            db, obj_in=booking_create, tenant_id=test_tenant.id
        )

        assert len(booking.services) == 1
        assert booking.services[0].service_id == test_services[0].id

    def test_create_booking_with_invalid_service(self, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test that booking creation fails with invalid service ID."""
        from fastapi import HTTPException

        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),
                ServiceItem(service_id=9999),  # Non-existent service
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Should fail"
        )

        with pytest.raises(HTTPException) as exc_info:
            booking_crud.create_with_tenant(
                db, obj_in=booking_create, tenant_id=test_tenant.id
            )
        assert exc_info.value.status_code == 400

    def test_booking_service_ids_property(self, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test the service_ids property on Booking."""
        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),
                ServiceItem(service_id=test_services[2].id),
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Multiple services"
        )

        booking = booking_crud.create_with_tenant(
            db, obj_in=booking_create, tenant_id=test_tenant.id
        )

        service_ids = booking.service_ids
        assert len(service_ids) == 2
        assert test_services[0].id in service_ids
        assert test_services[2].id in service_ids

    def test_total_revenue_calculation(self, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test that total revenue is calculated correctly with multiservice bookings."""
        # Create a completed multiservice booking
        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),  # $30
                ServiceItem(service_id=test_services[1].id),  # $75
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Full service"
        )

        booking = booking_crud.create_with_tenant(
            db, obj_in=booking_create, tenant_id=test_tenant.id
        )

        # Mark as completed
        from app.schemas.booking import BookingUpdate
        booking_update = BookingUpdate(status="completed")
        booking = booking_crud.update(db, db_obj=booking, obj_in=booking_update)

        # Query total revenue
        from sqlalchemy import func
        total_revenue = db.query(func.sum(BookingService.price)).\
            join(Booking, BookingService.booking_id == Booking.id).\
            filter(Booking.tenant_id == test_tenant.id, Booking.status == "completed").\
            scalar() or 0.0

        assert float(total_revenue) == 105.00  # $30 + $75


class TestBookingEndpointMultiservice:
    """Test booking API endpoints with multiservice support."""

    def test_create_booking_endpoint_multiservice(self, client: TestClient, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test POST /bookings/ with multiple services."""
        payload = {
            "customer_id": test_customer.id,
            "services": [
                {"service_id": test_services[0].id},
                {"service_id": test_services[1].id},
            ],
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "notes": "Endpoint test"
        }

        response = client.post(
            "/api/v1/bookings/",
            json=payload,
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["services"]) == 2
        assert data["status"] == "pending"

    def test_get_booking_endpoint_multiservice(self, client: TestClient, db: Session, test_tenant: Tenant, test_customer: Customer, test_services):
        """Test GET /bookings/{id} returns all services."""
        # Create a multiservice booking
        booking_create = BookingCreate(
            customer_id=test_customer.id,
            services=[
                ServiceItem(service_id=test_services[0].id),
                ServiceItem(service_id=test_services[2].id),
            ],
            user_id=None,
            start_time=datetime.now() + timedelta(days=1),
            notes="Test booking"
        )

        booking = booking_crud.create_with_tenant(
            db, obj_in=booking_create, tenant_id=test_tenant.id
        )

        response = client.get(
            f"/api/v1/bookings/{booking.id}",
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["services"]) == 2
