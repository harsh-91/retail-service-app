import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt  # Use `pyjwt` (install with `pip install PyJWT`)

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-for-dev")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # Typically "HS256"

security = HTTPBearer()

def decode_jwt(token: str):
    try:
        # Optionally: set verify_aud, verify_iss as needed for your deployment
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
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
    """
    Extracts current user and tenant context from JWT in Authorization: Bearer header.
    Returns a dict, e.g. {"username": ..., "tenant_id": ...}.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
        )
    payload = decode_jwt(credentials.credentials)
    # Customize these fields for your token claims!
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
        **payload  # In case you want extra info: roles, exp, etc.
    }
