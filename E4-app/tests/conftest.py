import os
import pytest
from flask import session
from app import app as flask_app

# Disable real monitoring dashboard binding during tests if needed
os.environ.setdefault('FLASK_ENV', 'testing')

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_session(client):
    """Creates a logged-in session with a syntactically valid (non-expired) unsigned JWT token.

    We disable signature verification in the app code, but jose still expects 3 base64url segments.
    Token contents: {"sub": "user", "exp": 1893456000} (far future to avoid expiry in tests).
    """
    fake_token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'  # {"alg":"HS256","typ":"JWT"}
        'eyJzdWIiOiJ1c2VyIiwiZXhwIjoxODkzNDU2MDAwfQ.'  # {"sub":"user","exp":1893456000}
        'c2ln'  # base64url('sig')
    )
    with client.session_transaction() as sess:
        sess['user_id'] = 'user'
        sess['username'] = 'user'
        sess['access_token'] = fake_token
        sess['token_type'] = 'bearer'
        sess['user_role'] = 'user'
    return client
