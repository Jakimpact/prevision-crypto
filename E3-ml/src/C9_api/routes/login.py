from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.C9_api.utils.auth import verify_password, create_access_token


router = APIRouter(
    prefix="/authentification",
    tags=["login"]
)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Vérifie un mot de passe et  et génère un token d'accès JWT."""
    if not verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
