from fastapi import APIRouter, Depends, Body

from src.C9_api.utils.deps import get_current_user
from src.C9_api.utils.classes import ForecastPairRequest
from src.C9_api.utils.functions import load_model


router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)


@router.post("/forecast_hourly")
def make_forecast_hourly(payload: ForecastPairRequest=Body(...), current_user=Depends(get_current_user)):
    """
    Charge un modèle de prévision et effectue une prévision horaire.
    Champs attendus dans le corps de la requête :
        trading_pair_symbol: Symbole de la paire de trading (par exemple, "BTC-USD")
        num_pred: Nombre de prévisions à effectuer (entre 1 et 24)
    """

    if payload.num_pred <= 0 or payload.num_pred > 24:
        raise ValueError("Le nombre de prévisions est invalide.")
    
    model = load_model(payload.trading_pair_symbol, "hour_models")
    forecast = model.predict(payload.num_pred)
    return {
        "trading_pair_symbol": payload.trading_pair_symbol,
        "num_pred": payload.num_pred,
        "forecast": forecast.values().flatten().tolist()
    }


@router.post("/forecast_daily")
def make_forecast_daily(payload: ForecastPairRequest=Body(...), current_user=Depends(get_current_user)):
    """
    Charge un modèle de prévision et effectue une prévision journalière.
    Champs attendus dans le corps de la requête :
        trading_pair_symbol: Symbole de la paire de trading (par exemple, "BTC-USD")
        num_pred: Nombre de prévisions à effectuer (entre 1 et 7)
    """

    if payload.num_pred <= 0 or payload.num_pred > 7:
        raise ValueError("Le nombre de prévisions est invalide.")
    
    model = load_model(payload.trading_pair_symbol, "day_models")
    forecast = model.predict(payload.num_pred)
    return {
        "trading_pair_symbol": payload.trading_pair_symbol,
        "num_pred": payload.num_pred,
        "forecast": forecast.values().flatten().tolist()
    }