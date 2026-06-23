from app.db.session import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import every model so SQLAlchemy registers them onto Base.metadata
#from app.models.tenant import Tenant
#from app.models.staff import Staff
#from app.models.service import Service
##from app.models.product import Product
# Import every model here so Alembic's autogenerate can discover them.
# Add a new line each time you create a model.
# from app.models.tenant import Tenant
# from app.models.user import User
# from app.models.staff import Staff
# from app.models.service import Service
# from app.models.customer import Customer
# from app.models.booking import Booking
# from app.models.product import Product
# from app.models.sale import Sale
