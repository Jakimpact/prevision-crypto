import requests

from src.settings import DataSettings
from src.utils.functions import get_jwt_token


def save_forecasts_to_db(pair_forecasters):
    """Enregistre les prévisions dans la base de données pour chaque forecaster."""

    for forecaster in pair_forecasters:
        jwt_token = get_jwt_token()
        if not jwt_token:
            raise Exception("Échec de la récupération du token JWT.")

        for date, row in forecaster.current_forecast.iterrows():
            post_data(forecaster, date, row["pred"], jwt_token)


def post_data(forecaster, date, forecast, token):
    """Envoie une prévision à l'API E1."""

    post_url = DataSettings.E1_api_post_forecast_urls[forecaster.granularity_type]
    payload = {
        "trading_pair_id": forecaster.trading_pair_id,
        "date": str(date),
        "value": str(forecast)
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(post_url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Erreur lors de l'envoi de la prévision : {response.status_code} - {response.text}")