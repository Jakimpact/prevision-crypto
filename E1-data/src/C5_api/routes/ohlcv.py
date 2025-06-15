from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db


router = APIRouter(
    prefix="/ohlcv",
    tags=["ohlcv"]
)


@router.get("/minute_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_minute_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données OHLCV à la minute pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    ohlcv_data = db.ohlcv_minute.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
    return ohlcv_data


@router.get("/hourly_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_hourly_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données OHLCV à l'heure pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    ohlcv_data = db.ohlcv_hourly.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
    return ohlcv_data


@router.get("/daily_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_daily_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données OHLCV au jour pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    ohlcv_data = db.ohlcv_daily.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
    return ohlcv_data