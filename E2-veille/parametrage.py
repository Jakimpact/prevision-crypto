"""Script de paramétrage pour appeler l'endpoint Trading Signals de Token Metrics.

Fonctionnalités:
 - Charge la clé d'API depuis le fichier .env (variable token_metrics_api_key)
 - Appelle l'endpoint https://api.tokenmetrics.com/v2/trading-signals
 - Construit un DataFrame pandas avec les champs principaux
 - Affiche le DataFrame dans la console
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import requests
import pandas as pd

BASE_DIR = Path(__file__).parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("token_metrics_api_key")
API_URL = "https://api.tokenmetrics.com/v2/trading-signals"


def main():
	try:
		data = fetch_trading_signals()
		df = build_dataframe(data)
		print(df.head(1))
	except Exception as e: 
		print("Erreur lors de l'exécution :", e)


def fetch_trading_signals():
	"""Appelle l'endpoint Trading Signals. Retourne la liste brute des objets JSON."""
	
	headers = {
		"accept": "application/json",
		"x-api-key": API_KEY
		}
	response = requests.get(API_URL, headers=headers)
	if response.status_code != 200:
		raise RuntimeError(
			f"Echec requête ({response.status_code}): {response.text}"
		)
	data = response.json()
	return data["data"]


def build_dataframe(data):
    """Construit un DataFrame filtré pour les cryptomonnaies voulues et les champs intéressants."""
	
    df = pd.DataFrame(data)
    df = df[["TOKEN_NAME", "TOKEN_SYMBOL", "DATE", "TRADING_SIGNAL", "TOKEN_TREND", "TRADING_SIGNALS_RETURNS", "HOLDING_RETURNS"]]
    return df


if __name__ == "__main__":
	main()

