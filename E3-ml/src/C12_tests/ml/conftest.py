# Configuration pytest spécifique pour les tests du pipeline ML
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

@pytest.fixture
def sample_ohlcv_data():
    """Fixture pour des données OHLCV mockées"""
    np.random.seed(42)  # Pour la reproductibilité
    dates = pd.date_range('2024-01-01', periods=100, freq='h')
    
    # Génération de données cohérentes et réalistes
    base_price = 50000
    price_variations = np.random.randn(100) * 50  # Variations plus petites
    
    closes = base_price + price_variations.cumsum()
    opens = closes + np.random.randn(100) * 10
    
    # Assurer que high >= max(open, close) et low <= min(open, close)
    highs = np.maximum(opens, closes) + np.abs(np.random.randn(100) * 20)
    lows = np.minimum(opens, closes) - np.abs(np.random.randn(100) * 20)
    
    # Assurer que tous les prix sont positifs
    lows = np.maximum(lows, 1)
    
    volumes = np.abs(np.random.randn(100) * 500 + 1000)  # Volumes positifs
    
    data = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    return data

@pytest.fixture
def sample_forecaster():
    """Fixture pour un forecaster mocké"""
    forecaster = Mock()
    forecaster.trading_pair_id = 1
    forecaster.granularity_type = "hour"
    forecaster.symbol = "BTC-USD"
    forecaster.freq = "h"
    forecaster.model_instance = Mock()
    forecaster.df_historical_data = None
    forecaster.ts_historical_data = None
    forecaster.historical_forecast = pd.DataFrame()
    forecaster.current_forecast = pd.DataFrame()
    forecaster.add_forecast_to_df = Mock()
    return forecaster

@pytest.fixture
def mock_timeseries():
    """Fixture pour une TimeSeries mockée"""
    from unittest.mock import MagicMock
    
    # Utilisation de MagicMock pour un support automatique des opérations magiques
    ts = MagicMock()
    
    # Mock pour la série "close" qui supporte aussi le slicing
    close_series = MagicMock()
    sliced_series = MagicMock()
    
    # Configuration des comportements
    ts.__getitem__.return_value = close_series  # Pour ts["close"]
    close_series.__getitem__.return_value = sliced_series  # Pour slicing [:training_end]
    
    # Propriétés communes
    ts.time_index = pd.date_range('2024-01-01', periods=50, freq='h')
    ts.values.return_value.flatten.return_value.tolist.return_value = [50000, 51000, 52000]
    ts.drop_before.return_value = ts
    ts.drop_after.return_value = ts
    ts.to_dataframe.return_value = pd.DataFrame({
        'close': np.random.randn(50) * 100 + 50000
    }, index=pd.date_range('2024-01-01', periods=50, freq='h'))
    ts.columns = ['close']
    
    # Configuration pour les objets retournés
    close_series.time_index = ts.time_index
    close_series.values = ts.values
    sliced_series.time_index = ts.time_index[:30]  # Simulation d'un slice
    sliced_series.values = ts.values
    
    return ts

@pytest.fixture
def mock_darts_model():
    """Fixture pour un modèle Darts mocké"""
    model = Mock()
    model.fit = Mock()
    model.predict = Mock(return_value=Mock(
        time_index=pd.date_range('2024-01-01', periods=3, freq='h'),
        values=Mock(return_value=Mock(flatten=Mock(return_value=Mock(tolist=Mock(return_value=[50000, 51000, 52000])))))
    ))
    model.score = Mock(return_value=0.85)
    return model

@pytest.fixture
def mock_jwt_token():
    """Fixture pour un token JWT mocké"""
    with patch('src.utils.functions.get_jwt_token') as mock_token:
        mock_token.return_value = "mock_jwt_token_123"
        yield mock_token

@pytest.fixture
def mock_api_responses():
    """Fixture pour mocker les réponses API"""
    with patch('requests.get') as mock_get:
        # Mock des données OHLCV
        mock_ohlcv_response = Mock()
        mock_ohlcv_response.status_code = 200
        mock_ohlcv_response.json.return_value = {
            "data": [
                {
                    "date": "2024-01-01T00:00:00",
                    "open": 50000.0,
                    "high": 50500.0,
                    "low": 49500.0,
                    "close": 50000.0,
                    "volume": 1000.0
                }
            ]
        }
        mock_ohlcv_response.raise_for_status = Mock()
        
        # Mock des dernières prévisions
        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            "data": [
                {
                    "date": "2024-01-01T01:00:00",
                    "forecast_value": 50100.0
                }
            ]
        }
        mock_forecast_response.raise_for_status = Mock()
        
        mock_get.return_value = mock_ohlcv_response
        yield mock_get

@pytest.fixture
def mock_settings():
    """Fixture pour mocker les settings"""
    with patch('src.C9_model.initiate_forecaster.HourModelsSettings') as mock_hour_settings, \
         patch('src.C9_model.initiate_forecaster.DayModelsSettings') as mock_day_settings:
        
        mock_hour_settings.pair_models = [
            {
                "trading_pair_id": 1,
                "symbol": "BTC-USD",
                "granularity_type": "hour",
                "freq": "h",
                "model_class": "RandomForest"
            }
        ]
        
        mock_day_settings.pair_models = [
            {
                "trading_pair_id": 1,
                "symbol": "BTC-USD", 
                "granularity_type": "day",
                "freq": "D",
                "model_class": "RandomForest"
            }
        ]
        
        yield mock_hour_settings, mock_day_settings

@pytest.fixture
def mock_trading_pair_forecaster():
    """Fixture pour mocker la classe TradingPairForecaster"""
    with patch('src.C9_model.initiate_forecaster.TradingPairForecaster') as mock_class:
        mock_instance = Mock()
        mock_instance.trading_pair_id = 1
        mock_instance.symbol = "BTC-USD"
        mock_instance.granularity_type = "hour"
        mock_instance.freq = "h"
        mock_instance.model_instance = Mock()
        mock_instance.df_historical_data = pd.DataFrame()
        mock_instance.ts_historical_data = Mock()
        mock_instance.historical_forecast = pd.DataFrame()
        mock_instance.current_forecast = pd.DataFrame()
        mock_instance.add_forecast_to_df = Mock()
        
        mock_class.return_value = mock_instance
        yield mock_class, mock_instance

@pytest.fixture
def mock_test_periods():
    """Fixture pour mocker les périodes de test"""
    test_periods = pd.DataFrame({
        'test_start': pd.date_range('2024-01-01', periods=3, freq='7D'),
        'test_end': pd.date_range('2024-01-08', periods=3, freq='7D')
    })
    return test_periods

@pytest.fixture 
def sample_forecast_data():
    """Fixture pour des données de prévision"""
    return pd.DataFrame({
        'forecast': [50000, 51000, 52000],
        'date': pd.date_range('2024-01-01', periods=3, freq='h')
    })

@pytest.fixture
def sample_metrics():
    """Fixture pour des métriques d'évaluation"""
    return {
        'mape': 5.2,
        'mae': 150.5,
        'direction_accuracy': 0.75
    }
