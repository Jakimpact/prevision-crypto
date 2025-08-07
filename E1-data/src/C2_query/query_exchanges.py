from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Exchange


@with_session
def get_all_exchanges(session: Session = None) -> List[Exchange]:
    """
    Récupère toutes les plateformes d'échange (exchanges).
    """
    return session.query(Exchange).all()


@with_session
def get_exchange_by_id(exchange_id: int, session: Session = None) -> Optional[Exchange]:
    """
    Récupère une plateforme d'échange par son identifiant.
    
    Filtrage : WHERE id = ...
    - Optimisation : index sur id pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Exchange).filter(Exchange.id == exchange_id).first()


@with_session
def get_exchange_by_name(name: str, session: Session = None) -> Optional[Exchange]:
    """
    Récupère une plateforme d'échange par son nom exact.
    
    Filtrage : WHERE name = ...
    - Optimisation : index sur name pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Exchange).filter(Exchange.name == name).first()


@with_session
def get_exchange_by_slug(slug: str, session: Session = None) -> Optional[Exchange]:
    """
    Récupère une plateforme d'échange par son slug exact.
    
    Filtrage : WHERE slug = ...
    - Optimisation : index sur slug pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Exchange).filter(Exchange.slug == slug).first()


@with_session
def search_exchanges(search_term: str, session: Session = None) -> List[Exchange]:
    """
    Recherche des plateformes d'échange par nom ou slug (recherche partielle).
    
    Filtrage : WHERE name ILIKE ... OR slug ILIKE ...
    - Utilise ilike pour la recherche insensible à la casse et partielle.
    """
    return (session.query(Exchange)
            .filter(
                (Exchange.name.ilike(f"%{search_term}%")) |
                (Exchange.slug.ilike(f"%{search_term}%"))
            )
            .all())