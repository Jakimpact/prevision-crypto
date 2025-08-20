"""
Tests pour l'API d'authentification
"""
import pytest
from src.C9_api.utils import auth as auth_utils
from fastapi import status


@pytest.mark.unit
class TestAuthEndpoints:
    """Tests pour les endpoints d'authentification"""

    def test_login_success(self, client):
        """Test de connexion réussie avec un mot de passe valide"""
        # Patch direct du mot de passe attendu
        auth_utils.STATIC_PASSWORD = "test_password"
        
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "test_user", "password": "test_password"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    def test_login_invalid_password(self, client):
        """Test de connexion échouée avec un mot de passe invalide"""
        auth_utils.STATIC_PASSWORD = "correct_password"
        
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
