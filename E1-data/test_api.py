import requests
from src.settings import SecretSettings

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/login"
TRADING_PAIRS_URL = f"{BASE_URL}/trading_pairs/trading_pairs_by_base_currency_symbol/BTC"
OHLCV_URL = f"{BASE_URL}/ohlcv/ohlcv_by_trading_pair_id/991" 

# 1. Authentification
login_data = {
    "username": SecretSettings.API_USERNAME,
    "password": SecretSettings.API_PASSWORD
}

response = requests.post(LOGIN_URL, data=login_data)
print("Login status:", response.status_code)
print("Login response:", response.text)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Appel de la route protégée
    resp = requests.get(TRADING_PAIRS_URL, headers=headers)
    print("Trading pairs status:", resp.status_code)
    print("Trading pairs response:", resp.text)

    resp = requests.get(OHLCV_URL, headers=headers)
    print("ohlcv status:", resp.status_code)
    print("ohlcv pairs response:", resp.text)
else:
    print("Échec de l'authentification, impossible de tester la route protégée.")
