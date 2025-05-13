from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV


@with_session
def get_all_crypto_csvs(session: Session) -> List[CryptocurrencyCSV]:
    """Récupère tous les fichiers CSV de cryptomonnaies"""
    return session.query(CryptocurrencyCSV).all()


@with_session
def get_crypto_csv_by_id(csv_id: int, session: Session) -> Optional[CryptocurrencyCSV]:
    """Récupère un fichier CSV par son ID"""
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.id == csv_id).first()


@with_session
def get_crypto_csvs_by_exchange(exchange_id: int, session: Session) -> List[CryptocurrencyCSV]:
    """Récupère tous les fichiers CSV pour un exchange donné"""
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.exchange_id == exchange_id).all()


@with_session
def get_crypto_csvs_by_trading_pair(trading_pair_id: int, session: Session) -> List[CryptocurrencyCSV]:
    """Récupère tous les fichiers CSV pour une paire de trading donnée"""
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id).all()


@with_session
def get_crypto_csvs_by_timeframe(timeframe: str, session: Session) -> List[CryptocurrencyCSV]:
    """Récupère tous les fichiers CSV pour un timeframe donné"""
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.timeframe == timeframe).all()


@with_session
def get_crypto_csvs_by_date_range(start_date: datetime, end_date: datetime, session: Session) -> List[CryptocurrencyCSV]:
    """Récupère tous les fichiers CSV dans une plage de dates donnée"""
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.start_date >= start_date)
            .filter(CryptocurrencyCSV.end_date <= end_date)
            .all())


@with_session
def get_crypto_csvs_by_trading_pair_and_timeframe(trading_pair_id: int, timeframe: str, session: Session) -> Optional[CryptocurrencyCSV]:
    """Récupère un fichier CSV spécifique par exchange, paire de trading et timeframe"""
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe == timeframe)
            .all())


@with_session
def get_crypto_csv_by_params(exchange_id: int, trading_pair_id: int, timeframe: str, session: Session) -> Optional[CryptocurrencyCSV]:
    """Récupère un fichier CSV spécifique par exchange, paire de trading et timeframe"""
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.exchange_id == exchange_id)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe == timeframe)
            .first())