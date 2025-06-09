from src.C4_database.database import Database
from typing import Generator


def get_db() -> Generator[Database, None, None]:
    """
    Dépendance FastAPI qui fournit une instance de la base de données.
    Garantit que la session est fermée après utilisation.
    """
    db = Database()
    try:
        yield db
    finally:
        db.session.close()
