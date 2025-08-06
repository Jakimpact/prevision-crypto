"""
Tests pour l'API d'authentification
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestAuthEndpoints:
    """Tests pour les endpoints d'authentification"""

    def test_login_success(self, client, monkeypatch):
        """Test de connexion réussie avec un mot de passe valide"""
        # Mock du mot de passe pour les tests
        monkeypatch.setenv("API_E3_PASSWORD", "test_password")
        
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "test_user", "password": "test_password"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    def test_login_invalid_password(self, client, monkeypatch):
        """Test de connexion échouée avec un mot de passe invalide"""
        monkeypatch.setenv("API_E3_PASSWORD", "correct_password")
        
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "test_user", "password": "wrong_password"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Incorrect password"

    def test_login_missing_credentials(self, client):
        """Test de connexion sans fournir de credentials"""
        response = client.post("/api/v1/authentification/login")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client):
        """Test de connexion avec username mais sans mot de passe"""
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "test_user"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
