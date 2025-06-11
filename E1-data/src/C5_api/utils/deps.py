from src.C4_database.database import Database

def get_db():
    """
    Dépendance FastAPI qui fournit une instance de la base de données.
    Garantit que la session est fermée après utilisation.
    """
    try:
        with Database() as db:
            yield db
    finally:
        db.session.close()