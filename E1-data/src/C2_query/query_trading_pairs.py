from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import TradingPair


@with_session
def get_all_trading_pairs(session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading.
    """
    return session.query(TradingPair).all()


@with_session
def get_trading_pair_by_id(trading_pair_id: int, session: Session = None) -> Optional[TradingPair]:
    """
    Récupère une paire de trading par son ID.
    
    Filtrage : WHERE id = ...
    - Optimisation : index sur id pour accélérer la recherche, first() limité la requête à un seul résultat.
    """
    return session.query(TradingPair).filter(TradingPair.id == trading_pair_id).first()


@with_session
def get_trading_pair_by_currencies(base_currency_id: int, quote_currency_id: int, session: Session = None) -> Optional[TradingPair]:
    """
    Récupère une paire de trading spécifique à partir des IDs des devises de base et de cotation.
    
    Filtrage : WHERE base_currency_id = ... AND quote_currency_id = ...
    - Optimisation : index sur base_currency_id et quote_currency_id pour accélérer la recherche.
    """
    return (session.query(TradingPair)
            .filter(TradingPair.base_currency_id == base_currency_id)
            .filter(TradingPair.quote_currency_id == quote_currency_id)
            .first())


@with_session
def get_trading_pairs_by_base_currency(base_currency_id: int, session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading pour une devise de base donnée.
    
    Filtrage : WHERE base_currency_id = ...
    - Optimisation : index sur base_currency_id pour accélérer la recherche.
    """
    return session.query(TradingPair).filter(TradingPair.base_currency_id == base_currency_id).all()


@with_session
def get_trading_pairs_by_quote_currency(quote_currency_id: int, session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading pour une devise de cotation donnée.
    
    Filtrage : WHERE quote_currency_id = ...
    - Optimisation : index sur quote_currency_id pour accélérer la recherche.
    """
    return session.query(TradingPair).filter(TradingPair.quote_currency_id == quote_currency_id).all()