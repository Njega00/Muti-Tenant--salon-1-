# app/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create the engine that communicates with Postgres
engine = create_engine(settings.DATABASE_URL)

# Create a session factory for handling requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models to inherit from
Base = declarative_base()

# Dependency to yield database sessions to our api endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        