from flask import url_for


def test_dashboard_requires_authentication(client):
    resp = client.get('/dashboard', follow_redirects=False)
    assert resp.status_code in (301, 302)


def test_dashboard_authenticated(app, authenticated_session):
    resp = authenticated_session.get('/dashboard')
    # Should be allowed (200 OK)
    assert resp.status_code == 200


def test_api_chart_data_requires_token(client):
    resp = client.get('/api/chart-data')
    assert resp.status_code == 401
    assert resp.is_json
    assert 'error' in resp.get_json()


def test_logout_clears_session(authenticated_session):
    resp = authenticated_session.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    resp2 = authenticated_session.get('/dashboard')
    assert resp2.status_code in (301, 302)
