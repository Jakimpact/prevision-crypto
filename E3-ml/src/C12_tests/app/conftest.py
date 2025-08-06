# Configuration pytest spécifique pour les tests de l'application Streamlit
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import requests

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

@pytest.fixture
def mock_requests_success():
    """Mock des requêtes HTTP réussies"""
    with patch('requests.post') as mock_post:
        # Mock pour le login
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"access_token": "test_token", "token_type": "bearer"}
        mock_login_response.raise_for_status.return_value = None
        
        # Mock pour le forecast
        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            "trading_pair_symbol": "BTC-USDT",
            "num_pred": 3,
            "forecast": [50000.0, 51000.0, 52000.0],
            "forecast_dates": ["2025-08-06T10:00:00", "2025-08-06T11:00:00", "2025-08-06T12:00:00"]
        }
        mock_forecast_response.raise_for_status.return_value = None
        
        # Configuration du mock pour retourner les bonnes réponses selon l'URL
        def side_effect(url, **kwargs):
            if "login" in url:
                return mock_login_response
            else:
                return mock_forecast_response
        
        mock_post.side_effect = side_effect
        yield mock_post

@pytest.fixture
def mock_requests_failure():
    """Mock des requêtes HTTP échouées"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def mock_settings():
    """Mock des settings pour les tests"""
    with patch('src.C10_app.utils.DataSettings') as mock_data_settings, \
         patch('src.C10_app.utils.SecretSettings') as mock_secret_settings:
        
        # Configuration des URLs mockées
        mock_data_settings.E3_api_login_url = "http://test-api/login"
        mock_data_settings.E3_api_post_forecast_urls = {
            "hourly": "http://test-api/forecast_hourly",
            "daily": "http://test-api/forecast_daily"
        }
        
        # Configuration des credentials mockés
        mock_secret_settings.API_E3_USERNAME = "test_user"
        mock_secret_settings.API_E3_PASSWORD = "test_password"
        
        yield mock_data_settings, mock_secret_settings
