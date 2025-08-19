import pytest
from services.forecast import forecast_service


def test_validate_params_success_hourly():
    valid, msg = forecast_service.validate_forecast_params('BTC-USDT', 'hourly', 5)
    assert valid is True
    assert msg == ''


def test_validate_params_invalid_pair():
    valid, msg = forecast_service.validate_forecast_params('DOGE-USDT', 'hourly', 5)
    assert not valid
    assert 'Paire non supportée' in msg


def test_validate_params_invalid_granularity():
    valid, msg = forecast_service.validate_forecast_params('BTC-USDT', 'weekly', 5)
    assert not valid
    assert 'Granularité non supportée' in msg


def test_validate_params_invalid_horizon_hourly():
    valid, msg = forecast_service.validate_forecast_params('BTC-USDT', 'hourly', 30)
    assert not valid
    assert 'horizon doit être entre 1 et 24' in msg


def test_validate_params_invalid_horizon_daily():
    valid, msg = forecast_service.validate_forecast_params('BTC-USDT', 'daily', 10)
    assert not valid
    assert 'horizon doit être entre 1 et 7' in msg
