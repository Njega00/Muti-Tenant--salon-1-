from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.connection import get_db, engine  
from app.models.auth import Base 
Base.metadata.create_all(bind=engine) 



app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.PROJECT_NAME, "docs": "/docs"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Execute a quick, low-overhead query to verify database connectivity
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "project": settings.PROJECT_NAME
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"error: {str(e)}"
        }
