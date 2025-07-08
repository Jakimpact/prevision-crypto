from darts import TimeSeries
import pandas as pd

from src.C9_model.train_model import train_model
from src.settings import logger, MLSettings


def make_forecasts(trading_pair_forecasters):
    """Effectue les prévisions pour chaque paire de trading et chaque granularité."""
    
    for forecaster in trading_pair_forecasters:
        for granularity in forecaster.granularities:

            forecasting_start = pd.to_datetime(MLSettings.dates_by_granularity[granularity["type"]]["forecasting_start"])
            forecasting_end = forecasting_start + pd.Timedelta((granularity["test_window"] - 1), unit=granularity["freq"])
            print(forecasting_start, forecasting_end)

            train_model(granularity["model_instance"], granularity["timeseries"], granularity["freq"], training_end=forecasting_start)
            forecast = make_forecast(granularity["model_instance"], granularity["freq"], forecasting_start, forecasting_end)
            forecaster.add_forecast_to_df(forecast, granularity, "current_forecast")


def make_forecast(model, freq, start, end):
    """Réalise des prévisions sur une période donnée et les retourne."""
    
    forecast = model.predict(len(pd.date_range(start, end, freq=freq)))
    return forecast