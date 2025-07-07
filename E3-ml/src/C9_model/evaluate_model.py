from darts.metrics import mape, mae
import pandas as pd

from src.C9_model.train_model import train_model
from src.C9_model.predict_model import make_forecast
from src.utils.functions import generate_test_periods



def test_past_performances(trading_pair_forecasters):
    """
    Pour chaque paire de trading et granularité, teste les performances des modèles dans le passé sur une période de test.
    Itère sur les périodes de test, entraine le modèle et calcule les performances par étape et au global.
    """

    daily_test_periods = generate_test_periods(granularity="daily")
    hourly_test_periods = generate_test_periods(granularity="hourly")

    for forecaster in trading_pair_forecasters:
        for granularity in forecaster.granularities:
            if granularity["type"] == "daily":
                test_periods = daily_test_periods
            elif granularity["type"] == "hourly":
                test_periods = hourly_test_periods

            for start, end in zip(test_periods["test_start"], test_periods["test_end"]):
                train_model(granularity["model_instance"], granularity["timeseries"], granularity["freq"], training_end=start)
                forecast = make_forecast(granularity["model_instance"], granularity["freq"], start, end)



            mape_score, mae_score = calculate_performance(granularity["timeseries"], forecast, granularity["freq"])
                

def calculate_performance(timeseries, forecast, freq):
    """Evalue les performances d'un modèle en utilisant la MAPE et la MAE sur une période donnée."""

    date_start = forecast.time_index.min() - pd.Timedelta(1, unit=freq)
    date_end = forecast.time_index.max() + pd.Timedelta(1, unit=freq)

    mape_score = round(mape(timeseries.drop_before(date_start).drop_after(date_end), forecast), 2)
    mae_score = round(mae(timeseries.drop_before(date_start).drop_after(date_end), forecast), 2)

    return mape_score, mae_score


def display_performance(start, end, mape, mae):
    """Affiche les performances d'un modèle sur une période donnée."""

    print(f"Prévision du {start} au {end} | MAPE -> {mape:.2f} | MAE -> {mae:.2f}")