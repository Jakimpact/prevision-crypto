from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import TradingPair


@with_session
def get_trading_pair_by_currencies(base_currency_id: int, quote_currency_id: int, session: Session = None) -> Optional[TradingPair]:
    """
    Récupère une paire de trading spécifique à partir des IDs des devises de base et de cotation.
    Filtrage sur base_currency_id et quote_currency_id, utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return (session.query(TradingPair)
            .filter(TradingPair.base_currency_id == base_currency_id)
            .filter(TradingPair.quote_currency_id == quote_currency_id)
            .first())