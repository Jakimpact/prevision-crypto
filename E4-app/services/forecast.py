import requests
import logging
from typing import Dict, Optional, Tuple, List
from config import Config
from utils.logger import logger as app_logger
import time

# Configuration du logging
logger = logging.getLogger(__name__)

class ForecastService:
    """Service pour les prévisions crypto via l'API E3"""
    
    def __init__(self):
        self.username = Config.E3_API_USERNAME
        self.password = Config.E3_API_PASSWORD
        self.timeout = 30
        self._token_cache = None
    
    def _get_e3_token(self) -> Tuple[bool, str]:
        """
        Authentifie et récupère le token JWT de l'API E3
        
        Returns:
            Tuple (success: bool, token: str)
        """
        try:
            data = {
                "username": self.username,
                "password": self.password
            }
            
            app_logger.log_info("Authentification auprès de l'API E3")
            
            # Mesure du temps de réponse
            start_time = time.time()
            response = requests.post(
                Config.ENDPOINTS_E3["login"],
                data=data,
                timeout=self.timeout
            )
            api_duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                app_logger.log_info("Authentification E3 réussie")
                app_logger.log_info(f"METRIC_API_CALL: E3_LOGIN - {api_duration:.3f}s - SUCCESS", include_user=False)
                return True, token
            else:
                app_logger.log_error(f"Erreur d'authentification E3: {response.status_code}")
                app_logger.log_info(f"METRIC_API_CALL: E3_LOGIN - {api_duration:.3f}s - FAILED", include_user=False)
                return False, ""
                
        except requests.exceptions.RequestException as e:
            app_logger.log_error(f"Erreur réseau lors de l'authentification E3: {str(e)}")
            return False, ""
        except Exception as e:
            app_logger.log_error(f"Erreur inattendue lors de l'authentification E3: {str(e)}")
            return False, ""
    
    def get_forecast(self, trading_pair: str, granularity: str, num_pred: int) -> Tuple[bool, Dict]:
        """
        Récupère les prévisions pour une paire donnée
        
        Args:
            trading_pair: Paire de trading (ex: "BTC-USDT", "ETH-USDT")
            granularity: "hourly" ou "daily"
            num_pred: Nombre de prédictions (1-24 pour hourly, 1-7 pour daily)
            
        Returns:
            Tuple (success: bool, result: dict)
        """
        try:
            # Authentification auprès d'E3
            auth_success, token = self._get_e3_token()
            if not auth_success:
                return False, {"error": "Impossible de s'authentifier auprès du service de prévision"}
            
            # Sélection de l'endpoint selon la granularité
            if granularity == "hourly":
                url = Config.ENDPOINTS_E3["forecast_hourly"]
            elif granularity == "daily":
                url = Config.ENDPOINTS_E3["forecast_daily"]
            else:
                return False, {"error": "Granularité non supportée"}
            
            # Préparation de la requête
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "trading_pair_symbol": trading_pair,
                "num_pred": num_pred
            }
            
            logger.info(f"Demande de prévision: {trading_pair}, {granularity}, {num_pred} prédictions")
            
            # Appel à l'API E3
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Prévision réussie pour {trading_pair}")
                return True, result
            else:
                logger.error(f"Erreur API E3: {response.status_code} - {response.text}")
                return False, {"error": f"Erreur du service de prévision: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de l'appel à l'API E3")
            return False, {"error": "Délai d'attente dépassé pour la prévision"}
            
        except requests.exceptions.ConnectionError:
            logger.error("Impossible de se connecter à l'API E3")
            return False, {"error": "Service de prévision temporairement indisponible"}
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la prévision: {str(e)}")
            return False, {"error": "Erreur interne lors de la prévision"}
    
    def validate_forecast_params(self, trading_pair: str, granularity: str, num_pred: int) -> Tuple[bool, str]:
        """
        Valide les paramètres de prévision
        
        Args:
            trading_pair: Paire de trading
            granularity: Granularité
            num_pred: Nombre de prédictions
            
        Returns:
            Tuple (valid: bool, error_message: str)
        """
        # Validation de la paire de trading
        valid_pairs = ["BTC-USDT", "ETH-USDT"]
        if trading_pair not in valid_pairs:
            return False, f"Paire non supportée. Paires disponibles: {', '.join(valid_pairs)}"
        
        # Validation de la granularité et des horizons
        if granularity == "hourly":
            if not (1 <= num_pred <= 24):
                return False, "Pour les prévisions horaires, l'horizon doit être entre 1 et 24 heures"
        elif granularity == "daily":
            if not (1 <= num_pred <= 7):
                return False, "Pour les prévisions journalières, l'horizon doit être entre 1 et 7 jours"
        else:
            return False, "Granularité non supportée. Utilisez 'hourly' ou 'daily'"
        
        return True, ""


# Instance globale du service
forecast_service = ForecastService()