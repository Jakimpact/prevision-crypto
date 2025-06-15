from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVMinute, TradingPair


@with_session
def get_all_pairs_from_ohlcv_minute(session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading qui ont des données dans OHLCVMinute"""
    return session.query(TradingPair)\
        .join(OHLCVMinute)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_minute_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVMinute]:
    """Récupère les données OHLCV minute pour une paire de trading spécifique"""
    return session.query(OHLCVMinute)\
        .filter(OHLCVMinute.trading_pair_id == trading_pair_id)\
        .all()