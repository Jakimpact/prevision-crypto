from src.C4_database.database import Database
from src.C5_api.utils.auth import get_password_hash
from src.settings import SecretSettings


def create_initial_api_user():
    """Crée un utilisateur API initial."""

    with Database() as db:
        # Vérifie si l'utilisateur API existe déjà
        existing_user = db.users.get_by_username(SecretSettings.API_USERNAME)
        if existing_user:
            return

        # Crée un nouvel utilisateur API
        user = db.users.create(
            username=SecretSettings.API_USERNAME,
            password_hashed=get_password_hash(SecretSettings.API_PASSWORD),
        )