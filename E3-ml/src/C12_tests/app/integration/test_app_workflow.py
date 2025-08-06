"""
Tests d'intégration pour l'application Streamlit
"""
import pytest
from unittest.mock import patch, Mock
import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))


@pytest.mark.integration
class TestAppWorkflow:
    """Tests d'intégration pour les workflows complets de l'application"""

    def test_complete_forecast_workflow_hourly(self, mock_requests_success, mock_settings):
        """Test du workflow complet pour une prévision horaire"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token, get_forecast
        
        # Étape 1: Récupération du token
        token = get_jwt_token()
        assert token == "test_token"
        
        # Étape 2: Prévision horaire
        forecast_url = mock_data_settings.E3_api_post_forecast_urls["hourly"]
        result = get_forecast(token, "BTC-USDT", 3, forecast_url)
        
        # Vérifications
        assert result["trading_pair_symbol"] == "BTC-USDT"
        assert result["num_pred"] == 3
        assert len(result["forecast"]) == 3
        assert len(result["forecast_dates"]) == 3
        
        # Vérification que les deux appels ont été faits
        assert mock_requests_success.call_count == 2

    def test_complete_forecast_workflow_daily(self, mock_requests_success, mock_settings):
        """Test du workflow complet pour une prévision journalière"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token, get_forecast
        
        # Étape 1: Récupération du token
        token = get_jwt_token()
        assert token == "test_token"
        
        # Étape 2: Prévision journalière
        forecast_url = mock_data_settings.E3_api_post_forecast_urls["daily"]
        result = get_forecast(token, "ETH-USDT", 7, forecast_url)
        
        # Vérifications
        assert result["trading_pair_symbol"] == "BTC-USDT"  # Du mock
        assert result["num_pred"] == 3  # Du mock
        
        # Vérification des paramètres envoyés
        call_args = mock_requests_success.call_args_list[-1]
        assert call_args[1]["json"]["trading_pair_symbol"] == "ETH-USDT"
        assert call_args[1]["json"]["num_pred"] == 7
        
        assert mock_requests_success.call_count == 2

    def test_workflow_with_authentication_failure(self, mock_requests_failure, mock_settings):
        """Test du workflow avec échec d'authentification"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token
        import requests
        
        # L'authentification doit échouer
        with pytest.raises(requests.exceptions.HTTPError):
            get_jwt_token()

    def test_workflow_with_forecast_failure(self, mock_settings):
        """Test du workflow avec échec de la prévision"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token, get_forecast
        import requests
        
        # Mock: login réussi, forecast échoué
        with patch('requests.post') as mock_post:
            # Premier appel (login) réussi
            mock_login_response = Mock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = {"access_token": "test_token"}
            mock_login_response.raise_for_status.return_value = None
            
            # Deuxième appel (forecast) échoué
            mock_forecast_response = Mock()
            mock_forecast_response.status_code = 500
            mock_forecast_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
            
            mock_post.side_effect = [mock_login_response, mock_forecast_response]
            
            # Login réussi
            token = get_jwt_token()
            assert token == "test_token"
            
            # Forecast échoué
            with pytest.raises(requests.exceptions.HTTPError):
                get_forecast(token, "BTC-USDT", 3, "http://test-api/forecast_hourly")

    def test_multiple_forecast_requests(self, mock_requests_success, mock_settings):
        """Test de plusieurs requêtes de prévision avec le même token"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token, get_forecast
        
        # Récupération du token une seule fois
        token = get_jwt_token()
        
        # Plusieurs prévisions avec le même token
        hourly_url = mock_data_settings.E3_api_post_forecast_urls["hourly"]
        daily_url = mock_data_settings.E3_api_post_forecast_urls["daily"]
        
        result1 = get_forecast(token, "BTC-USDT", 1, hourly_url)
        result2 = get_forecast(token, "ETH-USDT", 2, daily_url)
        result3 = get_forecast(token, "BTC-USDT", 5, hourly_url)
        
        # Vérifications
        assert all(r["trading_pair_symbol"] == "BTC-USDT" for r in [result1, result2, result3])
        
        # Vérification du nombre d'appels (1 login + 3 forecasts)
        assert mock_requests_success.call_count == 4

    def test_settings_integration(self, mock_settings):
        """Test de l'intégration avec les settings"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        # Vérification que les settings sont bien configurés
        assert mock_data_settings.E3_api_login_url == "http://test-api/login"
        assert "hourly" in mock_data_settings.E3_api_post_forecast_urls
        assert "daily" in mock_data_settings.E3_api_post_forecast_urls
        
        assert mock_secret_settings.API_E3_USERNAME == "test_user"
        assert mock_secret_settings.API_E3_PASSWORD == "test_password"

    def test_app_imports(self):
        """Test que tous les modules nécessaires peuvent être importés"""
        # Test des imports principaux
        try:
            from src.C10_app.utils import get_jwt_token, get_forecast
            from src.settings import DataSettings
            import streamlit as st
            import pandas as pd
            import requests
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_error_recovery_workflow(self, mock_settings):
        """Test de récupération après erreur"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        from src.C10_app.utils import get_jwt_token, get_forecast
        import requests
        
        with patch('requests.post') as mock_post:
            # Première tentative: échec
            mock_error_response = Mock()
            mock_error_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Error")
            
            # Deuxième tentative: succès
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.json.return_value = {"access_token": "recovered_token"}
            mock_success_response.raise_for_status.return_value = None
            
            mock_post.side_effect = [mock_error_response, mock_success_response]
            
            # Première tentative échoue
            with pytest.raises(requests.exceptions.HTTPError):
                get_jwt_token()
            
            # Deuxième tentative réussit
            token = get_jwt_token()
            assert token == "recovered_token"
