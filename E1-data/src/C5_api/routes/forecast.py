from fastapi import APIRouter, Depends, Body

from src.C5_api.utils.deps import get_current_user, get_db, require_role_script


router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)


@router.get("/minute_by_trading_pair_id/{trading_pair_id}")
def get_forecast_minute_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Prévisions minute d'une paire.
    Args:
        trading_pair_id: ID.
        start_date: Optionnel 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'.
    Returns:
        Liste JSON (peut être vide)."""
    forecast_data = db.forecast_minute.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/hourly_by_trading_pair_id/{trading_pair_id}")
def get_forecast_hourly_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Prévisions horaires d'une paire.
    Args:
        trading_pair_id: ID.
        start_date: Optionnel.
    Returns:
        Liste JSON (peut être vide)."""
    forecast_data = db.forecast_hourly.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/daily_by_trading_pair_id/{trading_pair_id}")
def get_forecast_daily_by_trading_pair(trading_pair_id: int, start_date: str=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Prévisions journalières d'une paire.
    Args:
        trading_pair_id: ID.
        start_date: Optionnel.
    Returns:
        Liste JSON (peut être vide)."""
    forecast_data = db.forecast_daily.get_forecast_by_trading_pair(trading_pair_id, start_date)
    return forecast_data


@router.get("/last_minute_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_minute_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Dernière prévision minute.
    Args:
        trading_pair_id: ID.
    Returns:
        Objet forecast ou null."""
    last_forecast = db.forecast_minute.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.get("/last_hourly_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_hourly_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Dernière prévision horaire.
    Args:
        trading_pair_id: ID.
    Returns:
        Objet forecast ou null."""
    last_forecast = db.forecast_hourly.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.get("/last_daily_by_trading_pair_id/{trading_pair_id}")
def get_last_forecast_daily_by_trading_pair(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Dernière prévision journalière.
    Args:
        trading_pair_id: ID.
    Returns:
        Objet forecast ou null."""
    last_forecast = db.forecast_daily.get_last_forecast_by_trading_pair(trading_pair_id)
    return last_forecast


@router.post("/minute")
def create_forecast_minute(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """Crée une prévision minute.
    Corps: trading_pair_id, date, value, model_name?, model_version?.
    Returns:
        Objet persisté."""
    obj = db.forecast_minute.create(**payload)
    return obj


@router.post("/hourly")
def create_forecast_hourly(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """Crée une prévision horaire.
    Corps: trading_pair_id, date, value, model_name?, model_version?.
    Returns:
        Objet persisté."""
    obj = db.forecast_hourly.create(**payload)
    return obj


@router.post("/daily")
def create_forecast_daily(
    payload: dict = Body(...),
    db=Depends(get_db),
    current_user=Depends(require_role_script)
):
    """Crée une prévision journalière.
    Corps: trading_pair_id, date, value, model_name?, model_version?.
    Returns:
        Objet persisté."""
    obj = db.forecast_daily.create(**payload)
    return obj

