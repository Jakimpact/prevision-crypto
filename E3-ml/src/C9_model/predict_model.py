from darts import TimeSeries
import pandas as pd

from src.C9_model.train_model import train_model
from src.C9_data.fetch_data import get_last_forecast_for_pair_forecaster
from src.settings import logger, MLSettings


def make_forecasts(pair_forecasters):
    """Effectue les prévisions pour chaque pair de forecasters."""

    for forecaster in pair_forecasters:
        last_historical_date = forecaster.df_historical_data.index[-1]
        last_forecast = get_last_forecast_for_pair_forecaster(forecaster)

        # Si aucune prévision n'existe, on va initialiser la table de la bdd avec la 1ere prévision
        if last_forecast is None:

            train_model(forecaster.model_instance, forecaster.ts_historical_data, 
                forecaster.freq, (last_historical_date + pd.Timedelta(1, unit=forecaster.freq)))
            forecast = forecaster.model_instance.predict(1)
            forecaster.add_forecast_to_df(forecast, "current_forecast")
        
        # Si une prévision existe, on va continuer à faire des prévisions jusqu'à la date de la dernière donnée historique
        else:
            last_forecast_date = last_forecast.date.iloc[0]
            
            while last_forecast_date <= last_historical_date:

                train_model(forecaster.model_instance, forecaster.ts_historical_data, 
                forecaster.freq, (last_forecast_date + pd.Timedelta(1, unit=forecaster.freq)))
                forecast = forecaster.model_instance.predict(1)
                forecaster.add_forecast_to_df(forecast, "current_forecast")

                last_forecast_date += pd.Timedelta(1, unit=forecaster.freq)


def make_forecasts_v0(trading_pair_forecasters):
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