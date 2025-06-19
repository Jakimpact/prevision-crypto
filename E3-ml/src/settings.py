import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


# Configure la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s')
logger = logging.getLogger("E3-ml")

BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "config/.env"))


def load_yaml_config(filename):
    config_path = BASE_DIR / "config" / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)
    

try:
    DATA_CONFIG = load_yaml_config("data_config.yaml")
except FileNotFoundError as e: 
    print(f"Warning: {e}")


class DataSettings():
    E1_API_LOGIN_URL = DATA_CONFIG["E1_API_URLS"]["E1_API_LOGIN_URL"]
    E1_API_OHLCV_URLS = DATA_CONFIG["E1_API_URLS"]["OHLCV_URLS"]
    
    DATA_GRANULARITIES = DATA_CONFIG["DATA_GRANULARITIES"]

    RAW_DATA_DIR_PATH = DATA_CONFIG["RAW_DATA_DIR_PATH"]

    TRADING_PAIRS = DATA_CONFIG["TRADING_PAIRS"]


class SecretSettings():
    API_USERNAME = os.getenv("API_USERNAME")
    API_PASSWORD = os.getenv("API_PASSWORD")


class LogSettings():
    LOG_PATH = os.path.join(BASE_DIR, "data/logs")