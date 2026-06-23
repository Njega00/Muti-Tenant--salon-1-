# app/db/base.py
# Import all models here so that Base.metadata can detect them cleanly
from app.db.connection import Base  # noqa
from app.models.tenant import Tenant  # noqa
from app.models.user import User  # noqa
from app.models.service import Service  # <--- Make sure this line is here!