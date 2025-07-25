from typing import List, Optional, Tuple

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


@with_session
def get_pairs_and_timeframes_from_historical_data(session: Session = None) -> List[Tuple[TradingPair, str]]:
    """
    Récupère toutes les paires de trading et leurs timeframes présents dans CSVHistoricalData.
    Retourne une liste de tuples (TradingPair, timeframe).
    """
    results = (
        session.query(TradingPair, CryptocurrencyCSV.timeframe)
        .join(CryptocurrencyCSV, CryptocurrencyCSV.trading_pair_id == TradingPair.id)
        .join(CSVHistoricalData, CSVHistoricalData.csv_file_id == CryptocurrencyCSV.id)
        .distinct()
        .all()
    )
    return results


@with_session
def get_historical_ohlcv_by_pair_id_and_timeframe(trading_pair_id: int, timeframe: str, session: Session = None) -> List[CSVHistoricalData]:
    """
    Récupère les données OHLCV historiques pour une paire de trading spécifique et un timeframe donné.
    """
    return (
        session.query(CSVHistoricalData)
        .join(CryptocurrencyCSV)
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
        .filter(CryptocurrencyCSV.timeframe == timeframe)
        .all()
    )