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
    HOUR_MODELS_CONFIG = load_yaml_config("hour_models_config.yaml")
    DAY_MODELS_CONFIG = load_yaml_config("day_models_config.yaml")
except FileNotFoundError as e: 
    print(f"Warning: {e}")


class DataSettings():
    E1_api_login_url = DATA_CONFIG["E1_api_urls"]["E1_api_login_url"]
    E1_api_ohlcv_urls = DATA_CONFIG["E1_api_urls"]["ohlcv_urls"]
    E1_api_get_all_forecast_urls = DATA_CONFIG["E1_api_urls"]["get_all_forecast_urls"]
    E1_api_get_last_forecast_urls = DATA_CONFIG["E1_api_urls"]["get_last_forecast_urls"]
    E1_api_post_forecast_urls = DATA_CONFIG["E1_api_urls"]["post_forecast_urls"]

    raw_data_dir_path = DATA_CONFIG["raw_data_dir_path"]
    models_dir_path = DATA_CONFIG["models_dir_path"]

    trading_pairs = DATA_CONFIG["trading_pairs"]


class MLSettings():
    trading_pairs = ML_CONFIG["trading_pairs"]
    date_formats = ML_CONFIG["date_formats"]
    dates_by_granularity = ML_CONFIG["dates_by_granularity"]
    models_config = ML_CONFIG["models_config"]


class HourModelsSettings():
    pair_models = HOUR_MODELS_CONFIG["pair_models"]


class DayModelsSettings():
    pair_models = DAY_MODELS_CONFIG["pair_models"]
    

class SecretSettings():
    API_USERNAME = os.getenv("API_USERNAME")
    API_PASSWORD = os.getenv("API_PASSWORD")
    SECRET_KEY = os.getenv("SECRET_KEY")
    API_E3_ALGORITHM = os.getenv("API_ALGORITHM")
    API_E3_USERNAME = os.getenv("API_E3_USERNAME")
    API_E3_PASSWORD = os.getenv("API_E3_PASSWORD")


class LogSettings():
    LOG_PATH = os.path.join(BASE_DIR, "data/logs")