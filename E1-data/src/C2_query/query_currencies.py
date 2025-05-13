from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import Currency


@with_session
def get_all_currencies(session: Session) -> List[Currency]:
    """Récupère toutes les devises de la base de données"""
    return session.query(Currency).all()


@with_session
def get_currency_by_id(currency_id: int, session: Session) -> Optional[Currency]:
    """Récupère une devise par son ID"""
    return session.query(Currency).filter(Currency.id == currency_id).first()


@with_session
def get_currency_by_name(name: str, session: Session) -> Optional[Currency]:
    """Récupère une devise par son nom"""
    return session.query(Currency).filter(Currency.name == name).first()


@with_session
def get_currency_by_symbol(symbol: str, session: Session) -> Optional[Currency]:
    """Récupère une devise par son symbole"""
    return session.query(Currency).filter(Currency.symbol == symbol).first()


@with_session
def get_currencies_by_type(currency_type: str, session: Session) -> List[Currency]:
    """Récupère toutes les devises d'un type donné (crypto ou fiat)"""
    return session.query(Currency).filter(Currency.type == currency_type).all()


@with_session
def get_top_cryptocurrencies(limit: int = 10, session: Session = None) -> List[Currency]:
    """Récupère les top N cryptomonnaies par rang"""
    return (session.query(Currency)
            .filter(Currency.type == "crypto")
            .filter(Currency.rank.isnot(None))
            .order_by(Currency.rank)
            .limit(limit)
            .all())


@with_session
def search_currencies_by_name(name_query: str, session: Session) -> List[Currency]:
    """Recherche des devises par nom (recherche partielle)"""
    return session.query(Currency).filter(Currency.name.ilike(f"%{name_query}%")).all()