from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV, CSVHistoricalData, TradingPair


@with_session
def get_all_pairs_from_historical_data(session: Session = None) -> List["TradingPair"]:
    """Récupère toutes les paires de trading qui ont des données dans CSVHistoricalData"""
    return session.query(TradingPair)\
        .join(CryptocurrencyCSV)\
        .join(CSVHistoricalData)\
        .distinct()\
        .all()


@with_session
def get_historical_ohlcv_by_pair_id(trading_pair_id: int, session: Session = None) -> List[CSVHistoricalData]:
    """Récupère les données OHLCV historiques pour une paire de trading spécifique"""
    return session.query(CSVHistoricalData)\
        .join(CryptocurrencyCSV)\
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)\
        .all()