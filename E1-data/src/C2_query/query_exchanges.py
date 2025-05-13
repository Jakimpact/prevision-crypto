from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Exchange


@with_session
def get_all_exchanges(session: Session) -> List[Exchange]:
    """Récupère tous les exchanges de la base de données"""
    return session.query(Exchange).all()


@with_session
def get_exchange_by_id(exchange_id: int, session: Session) -> Optional[Exchange]:
    """Récupère une plateforme d'échange par son ID"""
    return session.query(Exchange).filter(Exchange.id == exchange_id).first()


@with_session
def get_exchange_by_name( name: str, session: Session) -> Optional[Exchange]:
    """Récupère un exchange par son nom"""
    return session.query(Exchange).filter(Exchange.name == name).first()


@with_session
def get_exchange_by_slug(slug: str, session: Session) -> Optional[Exchange]:
    """Récupère un exchange par son slug"""
    return session.query(Exchange).filter(Exchange.slug == slug).first()


@with_session
def search_exchanges(search_term: str, session: Session) -> List[Exchange]:
    """Recherche des exchanges par nom ou slug (recherche partielle)"""
    return (session.query(Exchange)
            .filter(
                (Exchange.name.ilike(f"%{search_term}%")) |
                (Exchange.slug.ilike(f"%{search_term}%"))
            )
            .all())