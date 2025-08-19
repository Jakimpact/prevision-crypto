import json
from unittest.mock import patch


def test_forecast_route_validation(authenticated_session):
    resp = authenticated_session.post('/forecast', data={})
    assert resp.status_code == 200
    text = resp.data.decode('utf-8')
    assert 'Tous les champs sont requis' in text


def test_forecast_route_success(authenticated_session):
    fake_response = {
        'forecast_dates': ['2025-01-01T10:00:00Z'],
        'forecast': [123.45]
    }
    with patch('services.forecast.forecast_service.validate_forecast_params', return_value=(True, '')):
        with patch('services.forecast.forecast_service.get_forecast', return_value=(True, fake_response)):
            resp = authenticated_session.post('/forecast', data={
                'trading_pair': 'BTC-USDT',
                'granularity': 'hourly',
                'num_pred': '1'
            })
            assert resp.status_code == 200
            text = resp.data.decode('utf-8')
            assert 'Prévision réalisée avec succès' in text


def test_forecast_route_error(authenticated_session):
    with patch('services.forecast.forecast_service.validate_forecast_params', return_value=(True, '')):
        with patch('services.forecast.forecast_service.get_forecast', return_value=(False, {'error': 'Erreur X'})):
            resp = authenticated_session.post('/forecast', data={
                'trading_pair': 'BTC-USDT',
                'granularity': 'hourly',
                'num_pred': '1'
            })
            assert resp.status_code == 200
            text = resp.data.decode('utf-8')
            assert 'Erreur X' in text
