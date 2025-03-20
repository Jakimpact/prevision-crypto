from pathlib import Path

import yaml


BASE_DIR = Path(__file__).parent.parent


def load_yaml_config(filename):
    config_path = BASE_DIR / "config" / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)
    

try:
    EXTRACT_CONFIG = load_yaml_config("extract_config.yaml")
    DATABASE_CONFIG = load_yaml_config("database_config.yaml")
except FileNotFoundError as e: 
    print(f"Warning: {e}")


class ExtractSettings():
    pass

class DatabaseSettings():
    DB_PATH = DATABASE_CONFIG["db_path"]
    DB_FILENAME = DATABASE_CONFIG["db_filename"]