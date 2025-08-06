"""
Tests pour l'API de prévision (forecast)
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestForecastEndpoints:
    """Tests pour les endpoints de prévision"""

    def test_forecast_hourly_success(self, client, auth_headers):
        """Test de prévision horaire réussie"""
        # Mock du modèle et de la prévision
        mock_forecast = Mock()
        mock_forecast.values.return_value.flatten.return_value.tolist.return_value = [100.5, 101.2, 102.0]
        mock_forecast.time_index = ["2025-08-06T10:00:00", "2025-08-06T11:00:00", "2025-08-06T12:00:00"]
        
        mock_model = Mock()
        mock_model.predict.return_value = mock_forecast
        
        with patch('src.C9_api.routes.forecast.load_model', return_value=mock_model):
            payload = {
                "trading_pair_symbol": "BTC-USD",
                "num_pred": 3
            }
            
            response = client.post(
                "/api/v1/forecast/forecast_hourly",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["trading_pair_symbol"] == "BTC-USD"
            assert data["num_pred"] == 3
            assert len(data["forecast"]) == 3
            assert len(data["forecast_dates"]) == 3

    def test_forecast_hourly_invalid_num_pred_too_high(self, client, auth_headers):
        """Test de prévision horaire avec num_pred > 24"""
        payload = {
            "trading_pair_symbol": "BTC-USD",
            "num_pred": 25
        }
        
        # Capture l'exception ValueError directement
        with pytest.raises(ValueError, match="Le nombre de prévisions est invalide"):
            response = client.post(
                "/api/v1/forecast/forecast_hourly",
                json=payload,
                headers=auth_headers
            )

    def test_forecast_hourly_invalid_num_pred_zero(self, client, auth_headers):
        """Test de prévision horaire avec num_pred = 0"""
        payload = {
            "trading_pair_symbol": "BTC-USD",
            "num_pred": 0
        }
        
        # Capture l'exception ValueError directement
        with pytest.raises(ValueError, match="Le nombre de prévisions est invalide"):
            response = client.post(
                "/api/v1/forecast/forecast_hourly",
                json=payload,
                headers=auth_headers
            )

    def test_forecast_daily_success(self, client, auth_headers):
        """Test de prévision journalière réussie"""
        # Mock du modèle et de la prévision
        mock_forecast = Mock()
        mock_forecast.values.return_value.flatten.return_value.tolist.return_value = [50000.5, 51000.2]
        mock_forecast.time_index = ["2025-08-06", "2025-08-07"]
        
        mock_model = Mock()
        mock_model.predict.return_value = mock_forecast
        
        with patch('src.C9_api.routes.forecast.load_model', return_value=mock_model):
            payload = {
                "trading_pair_symbol": "BTC-USD",
                "num_pred": 2
            }
            
            response = client.post(
                "/api/v1/forecast/forecast_daily",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["trading_pair_symbol"] == "BTC-USD"
            assert data["num_pred"] == 2
            assert len(data["forecast"]) == 2
            assert len(data["forecast_dates"]) == 2

    def test_forecast_daily_invalid_num_pred_too_high(self, client, auth_headers):
        """Test de prévision journalière avec num_pred > 7"""
        payload = {
            "trading_pair_symbol": "BTC-USD",
            "num_pred": 8
        }
        
        # Capture l'exception ValueError directement
        with pytest.raises(ValueError, match="Le nombre de prévisions est invalide"):
            response = client.post(
                "/api/v1/forecast/forecast_daily",
                json=payload,
                headers=auth_headers
            )

    def test_forecast_hourly_unauthorized(self, client):
        """Test de prévision horaire sans authentification"""
        payload = {
            "trading_pair_symbol": "BTC-USD",
            "num_pred": 3
        }
        
        response = client.post(
            "/api/v1/forecast/forecast_hourly",
            json=payload
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forecast_daily_unauthorized(self, client):
        """Test de prévision journalière sans authentification"""
        payload = {
            "trading_pair_symbol": "BTC-USD",
            "num_pred": 2
        }
        
        response = client.post(
            "/api/v1/forecast/forecast_daily",
            json=payload
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forecast_invalid_payload(self, client, auth_headers):
        """Test avec un payload invalide"""
        payload = {
            "trading_pair_symbol": "BTC-USD"
            # num_pred manquant
        }
        
        response = client.post(
            "/api/v1/forecast/forecast_hourly",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_forecast_empty_payload(self, client, auth_headers):
        """Test avec un payload vide"""
        response = client.post(
            "/api/v1/forecast/forecast_hourly",
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
