from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVDaily, TradingPair


@with_session
def get_all_pairs_from_ohlcv_daily(session: Session = None) -> List[TradingPair]:
    """Récupère toutes les paires de trading qui ont des données dans OHLCVDaily"""
    return session.query(TradingPair)\
        .join(OHLCVDaily)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_daily_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVDaily]:
    """Récupère les données OHLCV daily pour une paire de trading spécifique"""
    return session.query(OHLCVDaily)\
        .filter(OHLCVDaily.trading_pair_id == trading_pair_id)\
        .all()


@with_session
def get_last_ohlcv_daily_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVDaily:
    """Récupère la dernière entrée OHLCV daily pour une paire de trading spécifique"""
    return session.query(OHLCVDaily)\
        .filter(OHLCVDaily.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVDaily.date.desc())\
        .first()
