from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import TradingPair


@with_session
def get_all_trading_pairs(session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading de la base de données"""
    return session.query(TradingPair).all()


@with_session
def get_trading_pair_by_id(trading_pair_id: int, session: Session = None) -> Optional[TradingPair]:
    """Récupère une paire de trading par son ID"""
    return session.query(TradingPair).filter(TradingPair.id == trading_pair_id).first()


@with_session
def get_trading_pair_by_currencies(base_currency_id: int, quote_currency_id: int, session: Session = None) -> Optional[TradingPair]:
    """Récupère une paire de trading spécifique à partir des IDs des devises de base et de cotation"""
    return (session.query(TradingPair)
            .filter(TradingPair.base_currency_id == base_currency_id)
            .filter(TradingPair.quote_currency_id == quote_currency_id)
            .first())


@with_session
def get_trading_pairs_by_base_currency(base_currency_id: int, session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading pour une devise de base donnée"""
    return session.query(TradingPair).filter(TradingPair.base_currency_id == base_currency_id).all()


@with_session
def get_trading_pairs_by_quote_currency(quote_currency_id: int, session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading pour une devise de cotation donnée"""
    return session.query(TradingPair).filter(TradingPair.quote_currency_id == quote_currency_id).all()