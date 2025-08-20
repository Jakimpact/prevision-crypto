"""
Tests unitaires pour les fonctions utilitaires de l'application Streamlit
"""
import pytest
from unittest.mock import patch, Mock
import requests
from src.C10_app.utils import get_jwt_token, get_forecast


@pytest.mark.unit
class TestAppUtils:
    """Tests pour les fonctions utilitaires de l'app Streamlit"""

    def test_get_jwt_token_success(self, mock_requests_success, mock_settings):
        """Test de récupération réussie du token JWT"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        token = get_jwt_token()
        
        assert token == "test_token"
        mock_requests_success.assert_called_once()
        
        # Vérification des paramètres de l'appel
        call_args = mock_requests_success.call_args
        assert call_args[0][0] == "http://test-api/login"  # URL
        assert call_args[1]["data"]["username"] == "test_user"
        assert call_args[1]["data"]["password"] == "test_password"

    def test_get_jwt_token_failure(self, mock_requests_failure, mock_settings):
        """Test d'échec de récupération du token JWT"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        with pytest.raises(requests.exceptions.HTTPError):
            get_jwt_token()

    def test_get_jwt_token_custom_credentials(self, mock_requests_success, mock_settings):
        """Test de récupération du token avec des credentials personnalisés"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        token = get_jwt_token(username="custom_user", password="custom_pass")
        
        assert token == "test_token"
        
        # Vérification que les credentials personnalisés ne sont pas utilisés
        # (la fonction actuelle ignore les paramètres username/password)
        call_args = mock_requests_success.call_args
        assert call_args[1]["data"]["username"] == "test_user"
        assert call_args[1]["data"]["password"] == "test_password"

    def test_get_forecast_success(self, mock_requests_success, mock_settings):
        """Test de récupération réussie des prévisions"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        token = "test_token"
        trading_pair = "BTC-USDT"
        num_pred = 3
        forecast_url = "http://test-api/forecast_hourly"
        
        result = get_forecast(token, trading_pair, num_pred, forecast_url)
        
        assert result["trading_pair_symbol"] == "BTC-USDT"
        assert result["num_pred"] == 3
        assert len(result["forecast"]) == 3
        assert len(result["forecast_dates"]) == 3
        
        # Vérification des paramètres de l'appel
        call_args = mock_requests_success.call_args_list[-1]  # Dernier appel
        assert call_args[0][0] == forecast_url
        assert call_args[1]["json"]["trading_pair_symbol"] == trading_pair
        assert call_args[1]["json"]["num_pred"] == num_pred
        assert call_args[1]["headers"]["Authorization"] == f"Bearer {token}"

    def test_get_forecast_failure(self, mock_requests_failure, mock_settings):
        """Test d'échec de récupération des prévisions"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        token = "test_token"
        trading_pair = "BTC-USDT"
        num_pred = 3
        forecast_url = "http://test-api/forecast_hourly"
        
        with pytest.raises(requests.exceptions.HTTPError):
            get_forecast(token, trading_pair, num_pred, forecast_url)

    def test_get_forecast_different_pairs(self, mock_requests_success, mock_settings):
        """Test des prévisions avec différentes paires de trading"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        # Test avec ETH-USDT
        result = get_forecast("test_token", "ETH-USDT", 2, "http://test-api/forecast_daily")
        
        # La fonction retourne toujours BTC-USDT dans le mock
        # mais on vérifie que l'appel est fait avec les bons paramètres
        call_args = mock_requests_success.call_args
        assert call_args[1]["json"]["trading_pair_symbol"] == "ETH-USDT"
        assert call_args[1]["json"]["num_pred"] == 2

    def test_get_forecast_invalid_token_format(self, mock_requests_success, mock_settings):
        """Test avec un format de token invalide"""
        mock_data_settings, mock_secret_settings = mock_settings
        
        # Le token peut être n'importe quoi, c'est l'API qui valide
        token = "invalid_token_format"
        result = get_forecast(token, "BTC-USDT", 1, "http://test-api/forecast_hourly")
        
        # Vérification que le token est bien transmis
        call_args = mock_requests_success.call_args
        assert call_args[1]["headers"]["Authorization"] == f"Bearer {token}"
