from typing import List, Optional
from sqlalchemy.orm import Session

from src.C4_database.models import Exchange


def get_all_exchanges(session: Session) -> List[Exchange]:
    """Récupère tous les exchanges de la base de données"""
    return session.query(Exchange).all()


def get_exchange_by_name(session: Session, name: str) -> Optional[Exchange]:
    """Récupère un exchange par son nom"""
    return session.query(Exchange).filter(Exchange.name == name).first()


def get_exchange_by_slug(session: Session, slug: str) -> Optional[Exchange]:
    """Récupère un exchange par son slug"""
    return session.query(Exchange).filter(Exchange.slug == slug).first()


def search_exchanges(session: Session, search_term: str) -> List[Exchange]:
    """Recherche des exchanges par nom ou slug (recherche partielle)"""
    return (session.query(Exchange)
            .filter(
                (Exchange.name.ilike(f"%{search_term}%")) |
                (Exchange.slug.ilike(f"%{search_term}%"))
            )
            .all())