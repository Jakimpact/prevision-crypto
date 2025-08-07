from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV


@with_session
def get_all_crypto_csvs(session: Session = None) -> List[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV de cryptomonnaies.
    """
    return session.query(CryptocurrencyCSV).all()


@with_session
def get_crypto_csv_by_id(csv_id: int, session: Session = None) -> Optional[CryptocurrencyCSV]:
    """
    Récupère un fichier CSV par son ID.
    
    Optimisation : Utilise un filtrage précis sur l'identifiant, first() limite la requête à un seul résultat.
    """
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.id == csv_id).first()


@with_session
def get_crypto_csvs_by_exchange(exchange_id: int, session: Session = None) -> List[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV pour un exchange donné.
    
    Optimisation : Filtrage direct sur exchange_id pour limiter la recherche aux fichiers pertinents.
    """
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.exchange_id == exchange_id).all()


@with_session
def get_crypto_csvs_by_trading_pair(trading_pair_id: int, session: Session = None) -> List[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV pour une paire de trading donnée.
    
    Optimisation : Filtrage direct sur trading_pair_id pour limiter la recherche aux fichiers pertinents.
    """
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id).all()


@with_session
def get_crypto_csvs_by_timeframe(timeframe: str, session: Session = None) -> List[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV pour un timeframe donné.
    
    Optimisation : Filtrage direct sur timeframe pour limiter la recherche aux fichiers pertinents.
    """
    return session.query(CryptocurrencyCSV).filter(CryptocurrencyCSV.timeframe == timeframe).all()


@with_session
def get_crypto_csvs_by_date_range(start_date: datetime, end_date: datetime, session: Session = None) -> List[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV dans une plage de dates donnée.
    
    Optimisation : Double filtrage sur start_date et end_date pour ne récupérer que les fichiers dans l'intervalle, évitant le chargement inutile de données hors plage.
    """
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.start_date >= start_date)
            .filter(CryptocurrencyCSV.end_date <= end_date)
            .all())


@with_session
def get_crypto_csvs_by_trading_pair_and_timeframe(trading_pair_id: int, timeframe: str, session: Session = None) -> Optional[CryptocurrencyCSV]:
    """
    Récupère tous les fichiers CSV pour une paire de trading et un timeframe donné.
    
    Optimisation : Filtrage combiné sur trading_pair_id et timeframe pour cibler précisément les fichiers recherchés.
    """
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe == timeframe)
            .all())


@with_session
def get_crypto_csv_by_params(exchange_id: int, trading_pair_id: int, timeframe: str, session: Session = None) -> Optional[CryptocurrencyCSV]:
    """
    Récupère un fichier CSV spécifique par exchange, paire de trading et timeframe.
    
    Optimisation : Filtrage multi-paramètres et .first() pour ne récupérer qu'un seul fichier correspondant, ce qui évite de charger une liste inutile.
    """
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.exchange_id == exchange_id)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe == timeframe)
            .first())


@with_session
def search_crypto_csvs_by_trading_pair_and_timeframe(trading_pair_id: int, timeframe: str, session: Session = None) -> Optional[CryptocurrencyCSV]:
    """
    Recherche tous les fichiers CSV pour une paire de trading et un timeframe donné.
    
    Optimisation : Filtrage sur trading_pair_id et recherche partielle sur timeframe avec .ilike pour permettre une flexibilité sur le format du timeframe.
    """
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe.ilike(f"%{timeframe}%"))
            .all())