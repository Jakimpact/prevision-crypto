from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV


@with_session
def search_crypto_csvs_by_trading_pair_and_timeframe(trading_pair_id: int, timeframe: str, session: Session = None) -> Optional[CryptocurrencyCSV]:
    """
    Recherche tous les fichiers CSV pour une paire de trading et un timeframe donné.
    Filtrage sur trading_pair_id et recherche partielle sur timeframe avec .ilike.
    """
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe.ilike(f"%{timeframe}%"))
            .all())