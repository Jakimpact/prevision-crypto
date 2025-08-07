from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Currency


@with_session
def get_currency_by_name(name: str, session: Session = None) -> Optional[Currency]:
    """
    Récupère une devise par son nom exact.
    Filtrage sur name, utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return session.query(Currency).filter(Currency.name == name).first()


@with_session
def get_currency_by_symbol(symbol: str, session: Session = None) -> Optional[Currency]:
    """
    Récupère une devise par son symbole exact.
    Filtrage sur symbol, utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return session.query(Currency).filter(Currency.symbol == symbol).first()