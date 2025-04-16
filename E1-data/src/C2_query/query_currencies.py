from typing import List, Optional
from sqlalchemy.orm import Session

from src.C4_database.models import Currency


def get_all_currencies(session: Session) -> List[Currency]:
    """Récupère toutes les devises de la base de données"""
    return session.query(Currency).all()


def get_currency_by_name(session: Session, name: str) -> Optional[Currency]:
    """Récupère une devise par son nom"""
    return session.query(Currency).filter(Currency.name == name).first()


def get_currency_by_symbol(session: Session, symbol: str) -> Optional[Currency]:
    """Récupère une devise par son symbole"""
    return session.query(Currency).filter(Currency.symbol == symbol).first()


def get_currencies_by_type(session: Session, currency_type: str) -> List[Currency]:
    """Récupère toutes les devises d'un type donné (crypto ou fiat)"""
    return session.query(Currency).filter(Currency.type == currency_type).all()


def get_top_cryptocurrencies(session: Session, limit: int = 10) -> List[Currency]:
    """Récupère les top N cryptomonnaies par rang"""
    return (session.query(Currency)
            .filter(Currency.type == "crypto")
            .filter(Currency.rank.isnot(None))
            .order_by(Currency.rank)
            .limit(limit)
            .all())


def search_currencies_by_name(session: Session, name_query: str) -> List[Currency]:
    """Recherche des devises par nom (recherche partielle)"""
    return session.query(Currency).filter(Currency.name.ilike(f"%{name_query}%")).all()