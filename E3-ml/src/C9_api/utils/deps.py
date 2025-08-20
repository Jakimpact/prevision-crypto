from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.C9_api.utils.auth import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/authentification/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dépendance FastAPI à partir du token JWT."""
    
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]
