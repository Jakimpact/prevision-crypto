import os
import requests
from typing import Optional

import pandas as pd

from src.settings import DataSettings, SecretSettings


def get_data_for_ml():
    """Récupère les données OHLCV pour les paires de trading renseignées et les enregistre en CSV."""
    
    # Récupération du token JWT pour l'authentification auprès de l'API E1
    jwt_token = get_jwt_token()
    if not jwt_token:
        raise Exception("Échec de la récupération du token JWT.")

    for trading_pair in DataSettings.TRADING_PAIRS:

        for granularity in DataSettings.DATA_GRANULARITIES:
            df = fetch_ohlcv(trading_pair["id"], trading_pair["start_date"], granularity, jwt_token)
            save_to_csv(df, trading_pair, granularity)


def get_jwt_token():
    """Récupère un token JWT depuis l'API E1."""
    
    login_url = DataSettings.E1_API_LOGIN_URL
    login_data = {
        "username": SecretSettings.API_USERNAME,
        "password": SecretSettings.API_PASSWORD
    }

    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Échec de la récupération du token JWT: {response.status_code} - {response.text}")


def fetch_ohlcv(trading_pair_id: int, start_date: Optional[str], granularity: str, token: str):
    """Récupère les données OHLCV pour une trading pair et les retourne sous forme de DataFrame."""
    
    ohlcv_url = DataSettings.E1_API_OHLCV_URLS[granularity] + f"/{trading_pair_id}"
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


def save_to_csv(df, trading_pair, granularity):
    """Enregistre les données OHLCV dans un fichier CSV."""
    
    csv_filename = f"ohlcv_{granularity}_{trading_pair['symbol']}.csv"
    os.makedirs(DataSettings.RAW_DATA_DIR_PATH, exist_ok=True)
    csv_file_path = DataSettings.RAW_DATA_DIR_PATH + f"/{csv_filename}"
    df.to_csv(csv_file_path, index=False)
    print(f"Données OHLCV pour {trading_pair['symbol']} enregistrées dans {csv_file_path}")