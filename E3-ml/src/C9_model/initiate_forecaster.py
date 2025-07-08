from darts import TimeSeries
from darts.utils.missing_values import fill_missing_values
import pandas as pd

from src.utils.classes import TradingPairForecaster
from src.settings import MLSettings
from src.utils.functions import load_ohlcv_csv


def initialize_trading_pairs_forecasters():
    """Initialise les pairs de trading à forecaster."""
    
    trading_pairs_forecasters = []

    for trading_pair_info in MLSettings.trading_pairs:
        forecaster = TradingPairForecaster(trading_pair_info)
        forecaster.initialize_granularities(trading_pair_info)
        for granularity in forecaster.granularities:
            df = load_ohlcv_csv(forecaster.symbol, granularity["type"])
            granularity["timeseries"] = time_series_transformation_steps(df, granularity["type"], granularity["freq"])

        trading_pairs_forecasters.append(forecaster)

    return trading_pairs_forecasters


def time_series_transformation_steps(df, granularity_type, freq):
    """A partir d'un dataframe, transforme les données en TimeSeries en appliquant différents traitements sur les données."""

    start_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["training_start"])
    end_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["forecasting_start"])

    df = df[(df.index >= start_date) & (df.index < end_date)]
    df = df.drop(columns=["trading_pair_id"])
    ts = TimeSeries.from_dataframe(df, freq=freq)
    ts = fill_missing_values(ts, fill="auto", method="time")
    return ts