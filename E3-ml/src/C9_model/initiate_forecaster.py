from darts import TimeSeries
from darts.utils.missing_values import fill_missing_values
import pandas as pd

from src.C9_data.fetch_data import get_data_for_pair_forecaster
from src.settings import MLSettings, HourModelsSettings, DayModelsSettings
from src.utils.classes import TradingPairForecaster, TradingPairForecaster_v0
from src.utils.functions import load_ohlcv_csv


def initialize_pair_forecasters_by_granularity(granularity):
    """Initialise les pairs de trading à forecaster, en fonction de la granularité."""

    if granularity == "hour":
        pair_models = HourModelsSettings.pair_models
    elif granularity == "day":
        pair_models = DayModelsSettings.pair_models

    pair_forecasters = []
    for pair_model_info in pair_models:
        forecaster = TradingPairForecaster(pair_model_info)
        df = get_data_for_pair_forecaster(forecaster)
        forecaster.df_historical_data = df.sort_values("date").set_index("date")
        forecaster.ts_historical_data = time_series_transformation_steps(forecaster.df_historical_data, forecaster.freq)
        pair_forecasters.append(forecaster)
    
    return pair_forecasters
        

def time_series_transformation_steps(df, freq):
    """A partir d'un dataframe, transforme les données en TimeSeries en appliquant différents traitements sur les données."""

    df = df.drop(columns=["trading_pair_id"])
    ts = TimeSeries.from_dataframe(df, freq=freq)
    ts = fill_missing_values(ts, fill="auto", method="time")
    return ts


def initialize_trading_pairs_forecasters():
    """Initialise les pairs de trading à forecaster."""
    
    trading_pairs_forecasters = []

    for trading_pair_info in MLSettings.trading_pairs:
        forecaster = TradingPairForecaster_v0(trading_pair_info)
        forecaster.initialize_granularities(trading_pair_info)
        for granularity in forecaster.granularities:
            df = load_ohlcv_csv(forecaster.symbol, granularity["type"])
            granularity["timeseries"] = time_series_transformation_steps_v0(df, granularity["type"], granularity["freq"])

        trading_pairs_forecasters.append(forecaster)

    return trading_pairs_forecasters


def time_series_transformation_steps_v0(df, granularity_type, freq):
    """A partir d'un dataframe, transforme les données en TimeSeries en appliquant différents traitements sur les données."""

    start_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["training_start"])
    end_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["forecasting_start"])

    df = df[(df.index >= start_date) & (df.index < end_date)]
    df = df.drop(columns=["trading_pair_id"])
    ts = TimeSeries.from_dataframe(df, freq=freq)
    ts = fill_missing_values(ts, fill="auto", method="time")
    return ts