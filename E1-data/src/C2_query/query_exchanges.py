from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Exchange


@with_session
def get_exchange_by_name(name: str, session: Session = None) -> Optional[Exchange]:
    """
    Récupère une plateforme d'échange par son nom exact.
    Filtrage sur name, utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return session.query(Exchange).filter(Exchange.name == name).first()