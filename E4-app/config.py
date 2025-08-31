import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
load_dotenv()


class Config:
    """Configuration de base pour l'application Flask"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('FLASK_APP_SECRET_KEY', 'dev-secret-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('FLASK_APP_SESSION_LIFETIME', '86400')))
    
    # URLs des APIs
    URL_E1 = os.getenv("API_E1_BASE_URL")
    URL_E3 = os.getenv("API_E3_BASE_URL")
    E3_API_USERNAME = os.getenv("E3_API_USERNAME")
    E3_API_PASSWORD = os.getenv("E3_API_PASSWORD")

    ENDPOINTS_E1 = {
        "login": f"{URL_E1}/api/v1/authentification/login",
        "register": f"{URL_E1}/api/v1/authentification/register",
        "trading_pair": f"{URL_E1}/api/v1/trading_pairs/trading_pair_by_currency_symbols",
        "ohlcv_hourly": f"{URL_E1}/api/v1/ohlcv/hourly_by_trading_pair_id",
        "ohlcv_daily": f"{URL_E1}/api/v1/ohlcv/daily_by_trading_pair_id",
        "forecast_hourly": f"{URL_E1}/api/v1/forecast/hourly_by_trading_pair_id",
        "forecast_daily": f"{URL_E1}/api/v1/forecast/daily_by_trading_pair_id",
    }

    ENDPOINTS_E3 = {
        "login": f"{URL_E3}/api/v1/authentification/login",
        "forecast_hourly": f"{URL_E3}/api/v1/forecast/forecast_hourly",
        "forecast_daily": f"{URL_E3}/api/v1/forecast/forecast_daily",
    }
    
    # Autres configurations
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # Configuration Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s'
    
    # Fichier de configuration du monitoring
    MONITORING_FILE_PATH = os.path.join(BASE_DIR, 'monitoring', 'config.cfg')

    # Configuration du monitoring via variables d'environnement
    MONITORING_DB_URI = os.getenv('MONITORING_DB_URI', f"sqlite:///{os.path.join(BASE_DIR, 'monitoring', 'dashboard.db')}")
    MONITORING_USERNAME = os.getenv('FLASK_MONITORING_USERNAME')
    MONITORING_PASSWORD = os.getenv('FLASK_MONITORING_PASSWORD')
    MONITORING_SECURITY_TOKEN = os.getenv('FLASK_MONITORING_SECURITY_TOKEN')

    # Seuils d'alerte (latence uniquement)
    THRESHOLDS = {
        "latency": {
            "forecast_ms": {"warning": 6000, "critical": 8000},
            "chart_data_ms": {"warning": 8500, "critical": 10000},
        }
    }


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False
    SECRET_KEY = os.getenv('FLASK_APP_SECRET_KEY')  # Obligatoire en production
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        # Vérifications supplémentaires pour la production
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")


# Sélection automatique de la configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}