import requests
import logging
from typing import Dict, Optional, Tuple
from config import Config

# Configuration du logging
logger = logging.getLogger(__name__)

class AuthService:
    """Service d'authentification avec l'API E1"""
    
    def __init__(self):
        self.base_url = Config.URL_E1
        self.timeout = 30
        
    def login(self, username: str, password: str) -> Tuple[bool, Dict]:
        """
        Authentifie un utilisateur via l'API E1
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Tuple (success: bool, response: dict)
        """
        url = Config.ENDPOINTS_E1["login"]
        
        # Données en format form-urlencoded selon l'OpenAPI
        data = {
            'username': username,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            logger.info(f"Tentative de connexion pour l'utilisateur: {username}")
            
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Connexion réussie pour: {username}")
                return True, result
            
            elif response.status_code == 401:
                error_data = response.json() if response.content else {'detail': 'Identifiants incorrects'}
                logger.warning(f"Échec de connexion pour {username}: {error_data.get('detail')}")
                return False, error_data
            
            else:
                error_msg = f"Erreur API E1: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return False, {'detail': error_msg}
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout lors de la connexion pour {username}")
            return False, {'detail': 'Délai d\'attente dépassé. Réessayez plus tard.'}
            
        except requests.exceptions.ConnectionError:
            logger.error("Impossible de se connecter à l'API E1")
            return False, {'detail': 'Service temporairement indisponible'}
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la connexion: {str(e)}")
            return False, {'detail': 'Erreur interne'}
    
    def register(self, username: str, password: str) -> Tuple[bool, Dict]:
        """
        Crée un nouveau compte utilisateur via l'API E1
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Tuple (success: bool, response: dict)
        """
        url = Config.ENDPOINTS_E1["register"]
        
        # Données en format JSON selon l'OpenAPI
        json_data = {
            'username': username,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Tentative d'inscription pour l'utilisateur: {username}")
            
            response = requests.post(
                url,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Inscription réussie pour: {username}")
                return True, result
            
            elif response.status_code == 400:
                error_data = response.json() if response.content else {'detail': 'Nom d\'utilisateur déjà existant'}
                logger.warning(f"Échec d'inscription pour {username}: {error_data.get('detail')}")
                return False, error_data
            
            else:
                error_msg = f"Erreur API E1: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return False, {'detail': error_msg}
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout lors de l'inscription pour {username}")
            return False, {'detail': 'Délai d\'attente dépassé. Réessayez plus tard.'}
            
        except requests.exceptions.ConnectionError:
            logger.error("Impossible de se connecter à l'API E1")
            return False, {'detail': 'Service temporairement indisponible'}
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'inscription: {str(e)}")
            return False, {'detail': 'Erreur interne'}


# Instance globale du service
auth_service = AuthService()