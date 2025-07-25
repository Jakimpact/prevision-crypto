from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVHourly, TradingPair


@with_session
def get_all_pairs_from_ohlcv_hourly(session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading qui ont des données dans OHLCVHourly"""
    return session.query(TradingPair)\
        .join(OHLCVHourly)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_hourly_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVHourly]:
    """Récupère les données OHLCV hourly pour une paire de trading spécifique"""
    return session.query(OHLCVHourly)\
        .filter(OHLCVHourly.trading_pair_id == trading_pair_id)\
        .all()


@with_session
def get_last_ohlcv_hourly_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVHourly:
    """Récupère la dernière entrée OHLCV hourly pour une paire de trading spécifique"""
    return session.query(OHLCVHourly)\
        .filter(OHLCVHourly.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVHourly.date.desc())\
        .first()
