import json
import os
import requests
from datetime import datetime

from src.settings import ExtractSettings


def extract_json(url, exchange, save_dir=ExtractSettings.JSON_PATH_CD):
    """Extrait un fichier JSON depuis une URL"""

    os.makedirs(save_dir, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    filename = f"{exchange}_crypo_data_ohlc.json"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w") as file:
        json.dump(json_data, file, indent=4)


def extract_jsons(json_urls=ExtractSettings.JSON_URLS):
    """Lance l'extraction de tout les fichiers json"""

    for item in json_urls:
        extract_json(url=json_urls[item], exchange=item)


def extract_csv():
    pass