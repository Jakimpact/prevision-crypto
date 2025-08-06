# Configuration pytest pour les tests de l'API
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.C9_api.api import app

@pytest.fixture
def client():
    """Fixture qui fournit un client de test FastAPI."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def valid_token(client):
    """Fixture qui fournit un token JWT valide pour les tests."""
    # Mock de l'authentification pour les tests
    from src.C9_api.utils.auth import create_access_token
    token = create_access_token(data={"sub": "test_user"})
    return token

@pytest.fixture
def auth_headers(valid_token):
    """Fixture qui fournit les headers d'authentification."""
    return {"Authorization": f"Bearer {valid_token}"}
