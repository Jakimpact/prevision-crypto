from utils.auth import is_authenticated, get_auth_headers, check_token_validity
from flask import session

FAKE_VALID_JWT = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'  # header
    'eyJzdWIiOiJ1c2VyIiwiZXhwIjoxODkzNDU2MDAwfQ.'  # payload with future exp
    'c2ln'  # signature placeholder
)


def test_is_authenticated_false_without_session(app):
    with app.test_request_context('/'):
        assert not is_authenticated()


def test_is_authenticated_true(app):
    with app.test_request_context('/'):
        session['user_id'] = 'user'
        session['username'] = 'user'
        session['access_token'] = FAKE_VALID_JWT
        session['token_type'] = 'bearer'
        assert is_authenticated()


def test_get_auth_headers_returns_headers(app):
    with app.test_request_context('/'):
        session['user_id'] = 'user'
        session['username'] = 'user'
        session['access_token'] = FAKE_VALID_JWT
        session['token_type'] = 'bearer'
        headers = get_auth_headers()
        assert headers is not None
        assert 'Authorization' in headers


def test_check_token_validity_valid(app):
    with app.test_request_context('/'):
        session['user_id'] = 'user'
        session['username'] = 'user'
        session['access_token'] = FAKE_VALID_JWT
        assert check_token_validity() is True


def test_check_token_validity_invalid_token(app):
    with app.test_request_context('/'):
        session['user_id'] = 'user'
        session['username'] = 'user'
        session['access_token'] = 'abc.def'  # malformed (no third segment)
        assert check_token_validity() is False
        assert 'user_id' not in session
