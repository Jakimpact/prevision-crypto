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
    ML_CONFIG = load_yaml_config("ml_config.yaml")
except FileNotFoundError as e: 
    print(f"Warning: {e}")


class DataSettings():
    E1_api_login_url = DATA_CONFIG["E1_api_urls"]["E1_api_login_url"]
    E1_api_ohlcv_urls = DATA_CONFIG["E1_api_urls"]["ohlcv_urls"]

    raw_data_dir_path = DATA_CONFIG["raw_data_dir_path"]

    trading_pairs = DATA_CONFIG["trading_pairs"]


class MLSettings():
    trading_pairs = ML_CONFIG["trading_pairs"]
    date_formats = ML_CONFIG["date_formats"]
    dates_by_granularity = ML_CONFIG["dates_by_granularity"]
    models_config = ML_CONFIG["models_config"]


class SecretSettings():
    API_USERNAME = os.getenv("API_USERNAME")
    API_PASSWORD = os.getenv("API_PASSWORD")


class LogSettings():
    LOG_PATH = os.path.join(BASE_DIR, "data/logs")