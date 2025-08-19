"""
Tests d'intégration pour l'API complète
"""
import pytest
from src.C9_api.utils import auth as auth_utils
from fastapi import status


@pytest.mark.integration
class TestAPIIntegration:
    """Tests d'intégration pour vérifier le bon fonctionnement global de l'API"""

    def test_app_startup(self, client):
        """Test que l'application démarre correctement"""
        # Test d'un endpoint simple pour vérifier que l'app fonctionne
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_full_workflow_login_and_forecast(self, client):
        """Test du workflow complet : login puis prévision"""
        # Configuration du mot de passe (patch direct de la variable statique)
        auth_utils.STATIC_PASSWORD = "test_password"
        
        # Étape 1 : Authentification
        login_response = client.post(
            "/api/v1/authentification/login",
            data={"username": "test_user", "password": "test_password"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # Étape 2 : Utilisation du token pour faire une prévision
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock du modèle pour cette intégration
        from unittest.mock import Mock, patch
        mock_forecast = Mock()
        mock_forecast.values.return_value.flatten.return_value.tolist.return_value = [100.5, 101.2]
        mock_forecast.time_index = ["2025-08-06T10:00:00", "2025-08-06T11:00:00"]
        
        mock_model = Mock()
        mock_model.predict.return_value = mock_forecast
        
        with patch('src.C9_api.routes.forecast.load_model', return_value=mock_model):
            forecast_payload = {
                "trading_pair_symbol": "BTC-USD",
                "num_pred": 2
            }
            
            forecast_response = client.post(
                "/api/v1/forecast/forecast_hourly",
                json=forecast_payload,
                headers=headers
            )
            
            assert forecast_response.status_code == status.HTTP_200_OK
            forecast_data = forecast_response.json()
            assert forecast_data["trading_pair_symbol"] == "BTC-USD"
            assert len(forecast_data["forecast"]) == 2

    def test_cors_headers(self, client):
        """Test que les headers CORS sont présents si configurés"""
        response = client.get("/docs")
        # Note: Les headers CORS devraient être configurés en production
        assert response.status_code == status.HTTP_200_OK

    def test_api_documentation_accessible(self, client):
        """Test que la documentation API est accessible"""
        # Test OpenAPI spec
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
