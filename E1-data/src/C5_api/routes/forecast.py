from fastapi import APIRouter, Depends, Body

from src.C5_api.utils.deps import get_current_user, get_db, require_role_script


router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)


@router.get("/minute_by_trading_pair_id/{trading_pair_id}")
def get_forecast_minute_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données forecast à la minute pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    forecast_data = db.forecast_minute.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/hourly_by_trading_pair_id/{trading_pair_id}")
def get_forecast_hourly_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données forecast à l'heure pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    forecast_data = db.forecast_hourly.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/daily_by_trading_pair_id/{trading_pair_id}")
def get_forecast_daily_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère les données forecast au jour pour une paire de trading spécifique.
    Si start_date est fourni, ne retourne que les données à partir de cette date.
    Args:
        trading_pair_id: ID de la paire de trading
        start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
    """
    forecast_data = db.forecast_daily.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/last_minute_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_minute_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère la dernière entrée forecast à la minute pour une paire de trading spécifique.
    """
    last_forecast = db.forecast_minute.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.get("/last_hourly_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_hourly_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère la dernière entrée forecast à l'heure pour une paire de trading spécifique.
    """
    last_forecast = db.forecast_hourly.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.get("/last_daily_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_daily_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """
    Récupère la dernière entrée forecast au jour pour une paire de trading spécifique.
    """
    last_forecast = db.forecast_daily.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.post("/minute")
def create_forecast_minute(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """
    Crée une entrée forecast minute.
    Champs attendus : trading_pair_id, date, value, model_name (optionnel), model_version (optionnel)
    """
    obj = db.forecast_minute.create(**payload)
    return obj


@router.post("/hourly")
def create_forecast_hourly(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """
    Crée une entrée forecast hourly.
    Champs attendus : trading_pair_id, date, value, model_name (optionnel), model_version (optionnel)
    """
    obj = db.forecast_hourly.create(**payload)
    return obj


@router.post("/daily")
def create_forecast_daily(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """
    Crée une entrée forecast daily.
    Champs attendus : trading_pair_id, date, value, model_name (optionnel), model_version (optionnel)
    """
    obj = db.forecast_daily.create(**payload)
    return obj

