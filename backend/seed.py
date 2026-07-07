# seed.py
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Resolve project backend directory path cleanly
sys.path.append(str(Path(__file__).resolve().parents[0]))

from app.db.connection import SessionLocal

# 1. Import the raw models
from app.models.tenant import Tenant
from app.models.user import User
from app.models.service import Service
from app.models.customer import Customer
from app.models.booking import Booking
from app.models.booking_service import BookingService

 

# ... (Step 1: imports remain the same) ...

# 2. 🔥 FORCE REGISTRATION IN BOTH REGISTRIES
tenant_registry = Tenant.registry._class_registry
user_registry = User.registry._class_registry

# Feed Tenant's world
tenant_registry["User"] = User
tenant_registry["Service"] = Service
tenant_registry["Customer"] = Customer
tenant_registry["Booking"] = Booking

# Feed User's world
user_registry["Tenant"] = Tenant
user_registry["Service"] = Service
user_registry["Customer"] = Customer
user_registry["Booking"] = Booking

# 3. Now compile the relationship mappings safely
from sqlalchemy.orm import configure_mappers
configure_mappers()
# 4. Grab security helper tools
from app.core.security import get_password_hash

# ... rest of your seed_database() function stays exactly the same ...
configure_mappers()

# 5. Grab security helper tools
from app.core.security import get_password_hash

def seed_database():
    print("⏳ Starting database seed sequence...")
    
    # 🚀 Import both engine AND Base directly here to guarantee scope access
    from app.db.connection import engine, Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Create a Premium Mock Tenant Workspace
        print("🏢 Seeding Tenant Workspace...")
        tenant = db.query(Tenant).filter(Tenant.name == "Executive Kings & Queens Salon").first()
        if not tenant:
            tenant = Tenant(
                name="Executive Kings & Queens Salon",
                subdomain="executive-kings"
                # 🚀 Removed 'is_active=True' to match your schema's columns perfectly!
            )
            db.add(tenant)
            db.flush()
        
        # 2. Create an Owner / Administrator Account
        print("👤 Seeding Staff & Administrative profiles...")
        owner = db.query(User).filter(User.email == "admin@executive.com").first()
        if not owner:
            owner = User(
                tenant_id=tenant.id,
                full_name="Alex Manager",
                email="admin@executive.com",
                hashed_password=get_password_hash("password123"),
                role="owner",
                is_active=True
            )
            db.add(owner)

        # Create a Stylist Staff Profile
        stylist = db.query(User).filter(User.email == "stylist@executive.com").first()
        if not stylist:
            stylist = User(
                tenant_id=tenant.id,
                full_name="Jane Barber",
                email="stylist@executive.com",
                hashed_password=get_password_hash("password123"),
                role="stylist",
                is_active=True
            )
            db.add(stylist)
            db.flush()

        # 3. Create a Standard Service Menu
        print("💇 Seeding Salon Service Menu catalog...")
        services_data = [
            {"name": "Fade Cut & Premium Wash", "price": 1500.0, "duration": 45},
            {"name": "Locs Retwist & Styling", "price": 4500.0, "duration": 120},
            {"name": "Gel Manicure & Polish", "price": 2000.0, "duration": 60},
            {"name": "Deep Conditioning Treatment", "price": 3000.0, "duration": 45}
        ]
        
        created_services = []
        for s_item in services_data:
            service = db.query(Service).filter(Service.name == s_item["name"], Service.tenant_id == tenant.id).first()
            if not service:
                service = Service(
                    tenant_id=tenant.id,
                    name=s_item["name"],
                    price=s_item["price"],
                    duration_minutes=s_item["duration"],
                    is_active=True
                )
                db.add(service)
                db.flush()
            created_services.append(service)

        # 4. Create Mock Customers
        print("👥 Seeding Client Rolodex...")
        customers_data = [
            {"full_name": "John Doe", "email": "john@gmail.com", "phone_number": "+254711111111"},
            {"full_name": "Alice Smith", "email": "alice@gmail.com", "phone_number": "+254722222222"}
        ]
        
        created_customers = []
        for c_item in customers_data:
            customer = db.query(Customer).filter(Customer.email == c_item["email"], Customer.tenant_id == tenant.id).first()
            if not customer:
                customer = Customer(
                    tenant_id=tenant.id,
                    full_name=c_item["full_name"],
                    email=c_item["email"],
                    phone_number=c_item["phone_number"],
                    is_active=True
                )
                db.add(customer)
                db.flush()
            created_customers.append(customer)

        # 5. Create Mock Bookings
        print("📅 Seeding Calendar Bookings timeline...")
        base_time = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        existing_booking = db.query(Booking).filter(Booking.tenant_id == tenant.id).first()
        if not existing_booking and created_services and created_customers:
            booking_1 = Booking(
                tenant_id=tenant.id,
                customer_id=created_customers[0].id,
                stylist_id=stylist.id,
                start_time=base_time,
                end_time=base_time + timedelta(minutes=created_services[0].duration_minutes),
                status="confirmed"
            )

            past_time = base_time - timedelta(days=2)
            booking_2 = Booking(
                tenant_id=tenant.id,
                customer_id=created_customers[1].id,
                stylist_id=stylist.id,
                start_time=past_time,
                end_time=past_time + timedelta(minutes=created_services[1].duration_minutes),
                status="completed"
            )
            db.add_all([booking_1, booking_2])
            db.flush()

            # create booking_services snapshots
            bs1 = BookingService(
                tenant_id=tenant.id,
                booking_id=booking_1.id,
                service_id=created_services[0].id,
                price=created_services[0].price,
                duration_minutes=created_services[0].duration_minutes
            )
            bs2 = BookingService(
                tenant_id=tenant.id,
                booking_id=booking_2.id,
                service_id=created_services[1].id,
                price=created_services[1].price,
                duration_minutes=created_services[1].duration_minutes
            )
            db.add_all([bs1, bs2])

        db.commit()
        print("✅ Database successfully populated with testing records!")

    except Exception as e:
        db.rollback()
        print(f"❌ Database seed aborted due to unexpected error: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()