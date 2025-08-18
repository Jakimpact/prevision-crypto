from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.settings import SecretSettings


# Configuration du hash de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Durée de validité du token (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hache le mot de passe en utilisant bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT avec les données fournies et une durée d'expiration optionnelle."""
    to_encode = data.copy()
    # Utiliser UTC pour éviter les problèmes de timezone
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SecretSettings.API_SECRET_KEY, algorithm=SecretSettings.API_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """Décode un token JWT et retourne les données du payload."""
    try:
        payload = jwt.decode(token, SecretSettings.API_SECRET_KEY, algorithms=[SecretSettings.API_ALGORITHM])           
        return payload
    except JWTError:
        return None
