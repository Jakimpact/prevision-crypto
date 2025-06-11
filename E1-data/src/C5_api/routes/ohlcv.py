from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db


router = APIRouter(
    prefix="/ohlcv",
    tags=["ohlcv"]
)


@router.get("/ohlcv_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données OHLCV pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    ohlcv_data = db.ohlcv.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
    return ohlcv_data