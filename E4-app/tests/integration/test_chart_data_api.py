from unittest.mock import patch


def test_chart_data_api_success(authenticated_session):
    with patch('services.ohlcv.OHLCVService.get_all_data', return_value=(
        [{'date': '2025-01-01T10:00:00Z', 'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume_quote': 10}],
        [{'date': '2025-01-01T11:00:00Z', 'value': 1.6, 'model_name': 'm', 'model_version': '1'}],
        {'id': 1}
    )), patch('services.ohlcv.OHLCVService.format_chart_data', return_value={
        'ohlcv': [{'date': '2025-01-01 11:00:00', 'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume': 10}],
        'forecasts': [{'date': '2025-01-01 12:00:00', 'value': 1.6}],
        'last_price': 1.5,
        'price_change': {'absolute': 0.1, 'percent': 7},
        'data_count': {'historical': 1, 'forecasts': 1}
    }):
        resp = authenticated_session.get('/api/chart-data?base=BTC&quote=USDT&granularity=hourly')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'trading_pair' in data
        assert data['data_count']['historical'] == 1


def test_chart_data_api_pair_not_found(authenticated_session):
    with patch('services.ohlcv.OHLCVService.get_all_data', return_value=([], [], None)):
        resp = authenticated_session.get('/api/chart-data?base=BTC&quote=FAKE&granularity=hourly')
        assert resp.status_code == 404
        assert resp.get_json()['error'].startswith('Paire de trading')


def test_chart_data_api_requires_token(client):
    # No auth: expect 401 JSON
    resp = client.get('/api/chart-data?base=BTC&quote=USDT&granularity=hourly')
    assert resp.status_code == 401
    assert 'error' in resp.get_json()
