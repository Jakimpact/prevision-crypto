import json
import requests
import os
from requests.exceptions import RequestException

from src.settings import ExtractSettings, logger, SecretSettings


def extract_maps(cmc_maps=ExtractSettings.CMC_MAPS):
    """Lance l'extraction de toutes les mappings nécéssaires depuis l'API de CoinMarketCap et les sauvegarde en json"""

    for map in cmc_maps:
        json = fetch_map(url=cmc_maps[map])
        save_to_json(data=json, type=map)


def fetch_map(url):
    """Extrait un mapping depuis l'API de CoinMarketCap"""

    api_key = SecretSettings.CMC_API_KEY
    if not api_key:
        raise ValueError("Une clé d'API valide est requise pour accéder à l'API de CoinMarketCap")
    
    headers = {
        'X-CMC_PRO_API_KEY': SecretSettings.CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Erreur durant la récupération des données : {e}")
        return None


def save_to_json(data, type, save_dir=ExtractSettings.JSON_PATH_CMC):
    """Sauvegarde les données sous un format JSON"""

    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"{type}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Erreur pendant la sauvegarde des données : {e}")