import os
import requests

import pandas as pd

from src.settings import DataSettings, MLSettings, SecretSettings


def get_jwt_token():
    """Récupère un token JWT depuis l'API E1."""
    
    login_url = DataSettings.E1_api_login_url
    login_data = {
        "username": SecretSettings.API_USERNAME,
        "password": SecretSettings.API_PASSWORD
    }

    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Échec de la récupération du token JWT: {response.status_code} - {response.text}")


def load_ohlcv_csv(trading_pair_symbol, granularity_type):
    """Charge un fichier CSV dans un DataFrame."""

    try:
        file_path = os.path.join(DataSettings.raw_data_dir_path, f"ohlcv_{granularity_type}_{trading_pair_symbol}.csv")
        df = pd.read_csv(file_path, sep=",", parse_dates=["date"], index_col="date")
        return df
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Le fichier {file_path} n'a pas été trouvé (erreur : {e}).")
    

def generate_test_periods(granularity_type):
    """Génère des périodes de test pour une granularité donnée."""

    start_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["test_start"])
    end_date = pd.to_datetime(MLSettings.dates_by_granularity[granularity_type]["test_end"])

    if granularity_type == "daily":
        freq = "D"
        test_window = 7
    elif granularity_type == "hourly":
        freq = "h"
        test_window = 24

    periods = []
    test_starts = pd.date_range(start=start_date, end=end_date-pd.Timedelta(days=test_window, unit=freq), freq=freq) # freq={test_window}{freq} pour des fenêtres non chevauchantes
    for test_start in test_starts:
        test_end = test_start + pd.Timedelta(test_window, unit=freq) - pd.Timedelta(1, unit=freq)
        periods.append({
            "test_start": test_start,
            "test_end": test_end
        })

    return pd.DataFrame(periods)