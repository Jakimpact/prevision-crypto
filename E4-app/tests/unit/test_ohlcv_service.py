from services.ohlcv import OHLCVService


def test_format_chart_data_basic():
    service = OHLCVService()
    ohlcv = [
        {'date': '2025-01-01T10:00:00Z', 'open': 10, 'high': 15, 'low': 9, 'close': 12, 'volume_quote': 100},
        {'date': '2025-01-01T11:00:00Z', 'open': 12, 'high': 16, 'low': 11, 'close': 14, 'volume_quote': 120},
    ]
    forecasts = [
        {'date': '2025-01-01T12:00:00Z', 'value': 15, 'model_name': 'm', 'model_version': '1'}
    ]

    result = service.format_chart_data(ohlcv, forecasts)
    assert result['last_price'] == 14
    assert result['data_count']['historical'] == 2
    assert result['data_count']['forecasts'] == 1
    assert result['price_change']['absolute'] == 2
    assert 'ohlcv' in result and 'forecasts' in result


def test_calculate_price_change_not_enough_data():
    service = OHLCVService()
    # Accès à la méthode privée via name mangling ou direct (pas strict ici)
    assert service._calculate_price_change([]) is None
    assert service._calculate_price_change([{'close': 10}]) is None
