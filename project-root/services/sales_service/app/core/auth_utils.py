import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt  # pip install PyJWT

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-for-dev")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()

def decode_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
        )
    payload = decode_jwt(credentials.credentials)
    username = payload.get("sub") or payload.get("username")
    tenant_id = payload.get("tenant_id")
    if not username or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: username or tenant_id missing",
        )
    return {
        "username": username,
        "tenant_id": tenant_id,
        **payload
    }

def get_current_tenant(current_user=Depends(get_current_user)) -> str:
    """
    Returns the tenant_id for the current authenticated user.
    """
    return current_user["tenant_id"]

