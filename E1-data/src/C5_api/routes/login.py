from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.C5_api.utils.auth import verify_password, create_access_token
from src.C4_database.database import Database
from src.C5_api.utils.deps import get_db


router = APIRouter(tags=["login"]
)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    """Authentifie un utilisateur et génère un token d'accès JWT."""

    user = db.users.get_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
