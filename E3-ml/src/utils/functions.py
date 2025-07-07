import os

import pandas as pd

from src.settings import DataSettings, MLSettings


def load_ohlcv_csv(trading_pair_symbol, granularity_type):
    """Charge un fichier CSV dans un DataFrame."""

    try:
        file_path = os.path.join(DataSettings.raw_data_dir_path, f"ohlcv_{granularity_type}_{trading_pair_symbol}.csv")
        df = pd.read_csv(file_path, sep=";", parse_dates=["date"], index_col="date")
        return df
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Le fichier {file_path} n'a pas été trouvé (erreur : {e}).")
    

def generate_test_periods(granularity_type):
    """Génère des périodes de test pour une granularité donnée."""

    start_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["test_start"], format=MLSettings.date_formats[granularity_type]["format"])
    end_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["test_end"], format=MLSettings.date_formats[granularity_type]["format"])

    if granularity_type == "daily":
        freq = "D"
        test_window = 7
    elif granularity_type == "hourly":
        freq = "H"
        test_window = 24

    periods = []
    test_starts = pd.date_range(start=start_date, end=end_date-pd.Timedelta(days=test_window, unit=freq), freq=freq)
    for test_start in test_starts:
        test_end = test_start + pd.Timedelta(test_window, unit=freq) - pd.Timedelta(1, unit=freq)
        periods.append({
            "test_start": test_start,
            "test_end": test_end
        })

    return pd.DataFrame(periods)