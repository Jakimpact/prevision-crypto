from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV, CSVHistoricalData, TradingPair


@with_session
def get_all_pairs_from_historical_data(session: Session = None) -> List["TradingPair"]:
    """
    Récupère toutes les paires de trading ayant des données historiques (CSVHistoricalData).
    
    Jointure multiple : TradingPair JOIN CryptocurrencyCSV JOIN CSVHistoricalData
    - Utilise .distinct() pour éviter les doublons et optimiser la requête.
    - Permet de ne sélectionner que les paires réellement présentes dans la table historique.
    - Optimisation : la jointure et le distinct évitent des scans inutiles.
    """
    return session.query(TradingPair)\
        .join(CryptocurrencyCSV)\
        .join(CSVHistoricalData)\
        .distinct()\
        .all()


@with_session
def get_historical_ohlcv_by_pair_id(trading_pair_id: int, session: Session = None) -> List[CSVHistoricalData]:
    """
    Récupère toutes les entrées OHLCV historiques pour une paire de trading donnée.
    
    Jointure : CSVHistoricalData JOIN CryptocurrencyCSV
    Filtrage : WHERE trading_pair_id = ...
    - Optimisation : requête simple, jointure directe, index sur trading_pair_id.
    """
    return session.query(CSVHistoricalData)\
        .join(CryptocurrencyCSV)\
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)\
        .all()


@with_session
def get_pairs_and_timeframes_from_historical_data(session: Session = None) -> List[Tuple[TradingPair, str]]:
    """
    Récupère toutes les paires de trading et leurs timeframes disponibles dans CSVHistoricalData.
    
    Jointure multiple : TradingPair JOIN CryptocurrencyCSV JOIN CSVHistoricalData
    - Utilise .distinct() pour éviter les doublons.
    - Retourne un tuple (TradingPair, timeframe) pour faciliter l'analyse multi-timeframe.
    - Optimisation : la jointure et le distinct évitent des scans inutiles.
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
    
    Jointure : CSVHistoricalData JOIN CryptocurrencyCSV
    Filtrage : WHERE trading_pair_id = ... AND timeframe = ...
    - Optimisation : index sur trading_pair_id pour accélérer la recherche.
    """
    return (
        session.query(CSVHistoricalData)
        .join(CryptocurrencyCSV)
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
        .filter(CryptocurrencyCSV.timeframe == timeframe)
        .all()
    )