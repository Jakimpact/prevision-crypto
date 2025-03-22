import json
import os
import requests
from datetime import datetime

from src.settings import EXTRACT_CONFIG, ExtractSettings


def extract_json(url, platform, save_dir=ExtractSettings.JSON_PATH):
    """Extrait un fichier JSON depuis une URL"""

    os.makedirs(save_dir, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    filename = f"{platform}_crypo_data_ohlc.json"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w") as file:
        json.dump(json_data, file, indent=4)


def extract_all_json(json_urls=ExtractSettings.JSON_URLS):
    """Lance l'extraction de tout les fichiers json"""

    for item in json_urls:
        extract_json(url=json_urls[item], platform=item)


def extract_csv():
    pass