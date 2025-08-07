from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Currency


@with_session
def get_all_currencies(session: Session = None) -> List[Currency]:
    """
    Récupère toutes les devises (cryptos et fiat).
    """
    return session.query(Currency).all()


@with_session
def get_currency_by_id(currency_id: int, session: Session = None) -> Optional[Currency]:
    """
    Récupère une devise par son identifiant.
    
    Filtrage : WHERE id = ...
    - Optimisation : index sur id pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Currency).filter(Currency.id == currency_id).first()


@with_session
def get_currency_by_name(name: str, session: Session = None) -> Optional[Currency]:
    """
    Récupère une devise par son nom exact.
    
    Filtrage : WHERE name = ...
    - Optimisation : index sur name pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Currency).filter(Currency.name == name).first()


@with_session
def get_currency_by_symbol(symbol: str, session: Session = None) -> Optional[Currency]:
    """
    Récupère une devise par son symbole exact.
    
    Filtrage : WHERE symbol = ...
    - Optimisation : index sur symbol pour accélérer la recherche, first() limite la requête à un seul résultat.
    """
    return session.query(Currency).filter(Currency.symbol == symbol).first()


@with_session
def get_currencies_by_type(currency_type: str, session: Session = None) -> List[Currency]:
    """
    Récupère les devises par type (crypto ou fiat).
    
    Filtrage : WHERE type = ...
    - Optimisation : index sur type pour accélérer la recherche.
    """
    return session.query(Currency).filter(Currency.type == currency_type).all()


@with_session
def get_top_cryptocurrencies(limit: int = 10, session: Session = None) -> List[Currency]:
    """
    Récupère les cryptomonnaies les mieux classées (par rank).
    
    Filtrage : WHERE type = 'crypto' AND rank IS NOT NULL
    - Utilise .order_by(Currency.rank) et .limit() pour optimiser la sélection des top-N.
    - Optimisation : index sur rank recommandé pour performance.
    """
    return (session.query(Currency)
            .filter(Currency.type == "crypto")
            .filter(Currency.rank.isnot(None))
            .order_by(Currency.rank)
            .limit(limit)
            .all())


@with_session
def search_currencies_by_name(name_query: str, session: Session = None) -> List[Currency]:
    """
    Recherche des devises par nom (recherche partielle).
    
    Filtrage : WHERE name ILIKE ...
    - Utilise ilike pour la recherche insensible à la casse et partielle.
    - Optimisation : index sur name recommandé pour performance.
    """
    return session.query(Currency).filter(Currency.name.ilike(f"%{name_query}%")).all()