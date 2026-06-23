from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.connection import get_db  # <-- Point directly to your primary connection utility

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

class CurrentUser:
    def __init__(self, user_id: int, tenant_id: int, role: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodes token using your internal security core
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_id = int(payload["sub"])
        tenant_id = int(payload["tenant_id"])
        role = payload["role"]
    except (JWTError, KeyError, ValueError):
        raise credentials_exc

    # Captures the tenant context on this specific connection thread for RLS policies
    db.execute(text("SET app.current_tenant = :tid"), {"tid": tenant_id})

    return CurrentUser(user_id=user_id, tenant_id=tenant_id, role=role)


def require_role(*allowed: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Insufficient permissions"
            )
        return user
    return checker