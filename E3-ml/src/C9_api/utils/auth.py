from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from src.settings import SecretSettings

ACCESS_TOKEN_EXPIRE_MINUTES = 30
STATIC_PASSWORD = SecretSettings.API_E3_PASSWORD


def verify_password(password: str) -> bool:
    """Vérifie si le mot de passe correspond."""
    return password == STATIC_PASSWORD


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT avec les données fournies et une durée d'expiration optionnelle."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SecretSettings.SECRET_KEY, algorithm=SecretSettings.API_E3_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """Décode un token JWT et retourne les données du payload."""
    try:
        payload = jwt.decode(token, SecretSettings.SECRET_KEY, algorithms=[SecretSettings.API_E3_ALGORITHM])
        return payload
    except JWTError:
        return None
