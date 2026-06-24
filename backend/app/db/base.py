# app/db/base.py
from app.db.connection import Base # noqa
from app.models.tenant import Tenant # noqa
from app.models.user import User # noqa
from app.models.service import Service # noqa
from app.models.customer import Customer # noqa
from app.models.booking import Booking # <--- Drop this line in here!