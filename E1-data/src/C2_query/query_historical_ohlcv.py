from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV, CSVHistoricalData, TradingPair


@with_session
def get_pairs_and_timeframes_from_historical_data(session: Session = None) -> List[Tuple[TradingPair, str]]:
    """
    Récupère toutes les paires de trading et leurs timeframes disponibles dans CSVHistoricalData.
    Jointure entre TradingPair, CryptocurrencyCSV et CSVHistoricalData, puis distinct pour éviter les doublons.
    Retourne un tuple (TradingPair, timeframe).
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
    Récupère les données OHLCV historiques pour une paire de trading et une timeframe donnée.
    Jointure entre CSVHistoricalData et CryptocurrencyCSV, filtrage sur trading_pair_id et timeframe.
    """
    return (
        session.query(CSVHistoricalData)
        .join(CryptocurrencyCSV)
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
        .filter(CryptocurrencyCSV.timeframe == timeframe)
        .all()
    )