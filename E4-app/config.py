import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))


class Config:
    """Configuration de base pour l'application Flask"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('SESSION_LIFETIME', '86400')))
    
    # URLs des APIs
    URL_E1 = os.getenv("URL_E1")
    URL_E3 = os.getenv("URL_E3")
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
    
    # Configuration Dash
    DASH_URL_BASE_PATHNAME = '/ui/'
    
    # Autres configurations
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Obligatoire en production
    
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