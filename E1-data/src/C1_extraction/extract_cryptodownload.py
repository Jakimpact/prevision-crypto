import json
import os
import requests
from datetime import datetime


def extract_json(url, save_dir, platform):
    """Extrait un fichier JSON depuis une URL"""

    os.makedirs(save_dir, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    filename = f"{platform}_crypo_data_ohlc.json"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w") as file:
        json.dump(json_data, file, indent=4)


def extract_csv():
    pass