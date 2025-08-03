import os
import requests
from typing import Optional

import pandas as pd

from src.settings import DataSettings
from src.utils.functions import get_jwt_token


def get_data_for_pair_forecaster(forecaster):
    """Récupère les données OHLCV pour une pair de trading et une granularité spécifique."""
    
    # Récupération du token JWT pour l'authentification auprès de l'API E1
    jwt_token = get_jwt_token()
    if not jwt_token:
        raise Exception("Échec de la récupération du token JWT.")

    df = fetch_ohlcv(forecaster.trading_pair_id, forecaster.granularity_type, jwt_token)
    return df


def get_last_forecast_for_pair_forecaster(forecaster):
    """Récupère la dernière prévision pour une pair de trading et une granularité spécifique."""
    
    jwt_token = get_jwt_token()
    if not jwt_token:
        raise Exception("Échec de la récupération du token JWT.")
    
    last_forecast = fetch_last_forecast(forecaster.trading_pair_id, forecaster.granularity_type, jwt_token)
    return last_forecast


def get_data_for_ml():
    """Récupère les données OHLCV pour les paires de trading renseignées et les enregistre en CSV."""
    
    # Récupération du token JWT pour l'authentification auprès de l'API E1
    jwt_token = get_jwt_token()
    if not jwt_token:
        raise Exception("Échec de la récupération du token JWT.")

    for trading_pair in DataSettings.trading_pairs:

        for granularity in trading_pair["data_granularities"]:
            df = fetch_ohlcv(trading_pair["id"], trading_pair["start_date"], granularity, jwt_token)
            save_to_csv(df, trading_pair, granularity)


def fetch_ohlcv(trading_pair_id: int, granularity: str, token: str, start_date: Optional[str]=None):
    """Récupère les données OHLCV pour une trading pair et les retourne sous forme de DataFrame."""
    
    ohlcv_url = DataSettings.E1_api_ohlcv_urls[granularity] + f"/{trading_pair_id}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"start_date": start_date} if start_date else {}
    response = requests.get(ohlcv_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        raise Exception(f"Échec de la récupération des données OHLCV: {response.status_code} - {response.text}")


def fetch_last_forecast(trading_pair_id: int, granularity: str, token: str):
    """Récupère la dernière prévision pour une trading pair et retourne un DataFrame."""
    
    last_forecast_url = DataSettings.E1_api_get_last_forecast_urls[granularity] + f"/{trading_pair_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(last_forecast_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data is None:
            return None
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        raise Exception(f"Échec de la récupération de la dernière prévision: {response.status_code} - {response.text}")


def save_to_csv(df, trading_pair, granularity):
    """Enregistre les données OHLCV dans un fichier CSV."""
    
    csv_filename = f"ohlcv_{granularity}_{trading_pair['symbol']}.csv"
    os.makedirs(DataSettings.raw_data_dir_path, exist_ok=True)
    csv_file_path = DataSettings.raw_data_dir_path + f"/{csv_filename}"
    df.to_csv(csv_file_path, index=False)
    print(f"Données OHLCV pour {trading_pair['symbol']} enregistrées dans {csv_file_path}")