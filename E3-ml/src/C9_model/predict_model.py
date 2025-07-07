import pandas as pd

from src.settings import logger


def make_forecasts(trading_pair_forecasters):
    """Effectue les prévisions pour chaque paire de trading et chaque granularité."""
    
    for forecaster in trading_pair_forecasters:
        for granularity in forecaster.granularities:
            model = granularity["model_instance"]

            predictions = model.predict()

            granularity["predictions"] = predictions
            logger.info(f"Prévisions effectuées pour {forecaster.base_currency}/{forecaster.quote_currency} à la granularité {granularity['type']}")



def make_forecast(model, freq, start, end):
    """Réalise des prévisions sur une période donnée et les retourne."""
    
    forecast = model.predict(len(pd.date_range(start, end, freq=freq)))
    return forecast