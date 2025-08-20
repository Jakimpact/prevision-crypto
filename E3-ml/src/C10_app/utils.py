import requests

from src.settings import DataSettings, SecretSettings

def get_jwt_token(username: str=None, password: str=None) -> str:
    """Récupère le JWT Token via le endpoint login."""
    data = {
        "username": SecretSettings.API_E3_USERNAME,
        "password": SecretSettings.API_E3_PASSWORD
    }
    response = requests.post(DataSettings.E3_api_login_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_forecast(token: str, trading_pair_symbol: str, num_pred: int, forecast_url: str):
    """Appelle le endpoint forecast pour la granularité voulue."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "trading_pair_symbol": trading_pair_symbol,
        "num_pred": num_pred
    }
    response = requests.post(forecast_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

