# backend/MULTISERVICE_MIGRATION.md
# Multiservice Bookings Implementation Guide

## Database Schema Changes

This document describes the changes needed to support multiservice appointments.

### New Model: BookingService

The `BookingService` table is a junction/association table linking bookings to services:

```sql
CREATE TABLE booking_services (
    id INTEGER PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    price DECIMAL(10, 2),  -- Snapshot of service price at booking time
    duration_minutes INTEGER,  -- Snapshot of service duration
    sequence_order INTEGER DEFAULT 1,  -- Order in the booking sequence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);
```

**Note:** The `booking_services` table includes a `tenant_id` column for multi-tenant isolation if needed.

### Modified Model: Booking

- **Removed:** `service_id` column (previously a single FK to services table)
- **Added:** `services` relationship to `BookingService` (one-to-many)
- **Added:** `service_ids` property for backward compatibility

### Schema Migration Steps

1. Create `booking_services` table
2. Migrate existing bookings: For each booking with a single service_id, create a corresponding BookingService row
3. Drop `service_id` column from `bookings` table

### Auto-Migration

The models are defined in SQLAlchemy and will be created automatically on first run if using:
```python
from app.db.connection import engine
from app.db.base import Base
Base.metadata.create_all(bind=engine)
```

Or manually via alembic:
```bash
cd backend
alembic revision --autogenerate -m "Add multiservice bookings support"
alembic upgrade head
```

## API Changes

### Creating a Booking (Before)
```json
POST /api/v1/bookings/
{
  "customer_id": 1,
  "service_id": 2,
  "start_time": "2026-07-01T10:00:00",
  "user_id": 3,
  "notes": "Regular haircut"
}
```

### Creating a Booking (After)
```json
POST /api/v1/bookings/
{
  "customer_id": 1,
  "services": [
    {"service_id": 2},
    {"service_id": 5}
  ],
  "start_time": "2026-07-01T10:00:00",
  "user_id": 3,
  "notes": "Haircut and coloring"
}
```

### Response Format
```json
{
  "id": 10,
  "tenant_id": 1,
  "customer_id": 1,
  "stylist_id": 3,
  "start_time": "2026-07-01T10:00:00",
  "end_time": "2026-07-01T11:30:00",
  "status": "pending",
  "notes": "Haircut and coloring",
  "services": [
    {
      "service_id": 2,
      "price": 30.00,
      "duration_minutes": 30
    },
    {
      "service_id": 5,
      "price": 75.00,
      "duration_minutes": 60
    }
  ],
  "created_at": "2026-07-01T09:00:00"
}
```

## Revenue Calculation

Total revenue per booking is now the sum of `BookingService.price` snapshots:

```python
# Old (single service)
total_revenue = db.query(func.sum(Service.price)).\
    join(Booking, Booking.service_id == Service.id).\
    filter(Booking.tenant_id == tenant_id).\
    scalar()

# New (multiple services)
total_revenue = db.query(func.sum(BookingService.price)).\
    join(Booking, BookingService.booking_id == Booking.id).\
    filter(Booking.tenant_id == tenant_id).\
    scalar()
```

## Backward Compatibility

- Single-service bookings still work: pass a list with one service item
- The `Booking.service_ids` property returns a list of service IDs for convenience
- Existing client code that expects a single `service_id` must be updated to expect `services` list

## Testing

Run the multiservice test suite:
```bash
cd backend
pytest tests/test_multiservice_bookings.py -v
```
