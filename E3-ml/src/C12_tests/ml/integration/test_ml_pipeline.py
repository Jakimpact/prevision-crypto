"""
Tests d'intégration pour le pipeline ML complet
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))


@pytest.mark.integration
@pytest.mark.ml
class TestMLPipelineIntegration:
    """Tests d'intégration pour le pipeline ML complet"""

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    @patch('src.C9_model.initiate_forecaster.time_series_transformation_steps')
    def test_complete_pipeline_hourly(self, mock_transform, mock_get_data, 
                                    mock_settings, mock_trading_pair_forecaster,
                                    sample_ohlcv_data, mock_timeseries):
        """Test du pipeline complet pour la granularité horaire"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        from src.C9_model.predict_model import make_forecasts
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        mock_transform.return_value = mock_timeseries
        
        # Étape 1: Initialisation des forecasters
        pair_forecasters = initialize_pair_forecasters_by_granularity("hour")
        
        # Étape 2: Prédictions
        with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model') as mock_train:
            
            mock_get_last.return_value = None
            mock_forecast = Mock()
            mock_instance.model_instance.predict.return_value = mock_forecast
            
            make_forecasts(pair_forecasters)
        
        # Vérifications
        assert len(pair_forecasters) == 1
        mock_instance.add_forecast_to_df.assert_called_with(mock_forecast, "current_forecast")

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    @patch('src.C9_model.initiate_forecaster.time_series_transformation_steps')
    def test_complete_pipeline_daily(self, mock_transform, mock_get_data,
                                   mock_settings, mock_trading_pair_forecaster,
                                   sample_ohlcv_data, mock_timeseries):
        """Test du pipeline complet pour la granularité journalière"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        from src.C9_model.predict_model import make_forecasts
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        mock_transform.return_value = mock_timeseries
        
        # Test pour granularité daily
        pair_forecasters = initialize_pair_forecasters_by_granularity("day")
        
        with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model'):
            
            mock_get_last.return_value = None
            mock_instance.model_instance.predict.return_value = Mock()
            
            make_forecasts(pair_forecasters)
        
        assert len(pair_forecasters) == 1

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    @patch('src.C9_model.initiate_forecaster.time_series_transformation_steps')
    def test_pipeline_with_evaluation(self, mock_transform, mock_get_data,
                                    mock_settings, mock_trading_pair_forecaster,
                                    sample_ohlcv_data, mock_timeseries, sample_metrics):
        """Test du pipeline avec évaluation des performances"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        from src.C9_model.evaluate_model import test_forecaster_past_performances
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        mock_transform.return_value = mock_timeseries
        
        # Initialisation
        pair_forecasters = initialize_pair_forecasters_by_granularity("hour")
        
        # Évaluation avec mocks
        with patch('src.C9_model.evaluate_model.generate_test_periods') as mock_periods, \
             patch('src.C9_model.evaluate_model.train_model'), \
             patch('src.C9_model.evaluate_model.make_forecast'), \
             patch('src.C9_model.evaluate_model.calculate_metrics') as mock_calc:
            
            mock_periods.return_value = pd.DataFrame({
                'test_start': [pd.Timestamp('2024-01-01')],
                'test_end': [pd.Timestamp('2024-01-02')]
            })
            mock_calc.return_value = (sample_metrics['mape'], 
                                    sample_metrics['mae'], 
                                    sample_metrics['direction_accuracy'])
            
            forecaster = pair_forecasters[0]
            mape, mae, direction_acc = test_forecaster_past_performances(forecaster)
            
            # Vérifications
            assert mape == sample_metrics['mape']
            assert mae == sample_metrics['mae']
            assert direction_acc == sample_metrics['direction_accuracy']

    def test_pipeline_data_flow(self, mock_settings, mock_trading_pair_forecaster, sample_ohlcv_data):
        """Test du flux de données dans le pipeline"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        
        with patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster') as mock_get_data, \
             patch('src.C9_model.initiate_forecaster.time_series_transformation_steps') as mock_transform:
            
            mock_get_data.return_value = sample_ohlcv_data
            mock_ts = Mock()
            mock_transform.return_value = mock_ts
            
            # Test du flux
            forecasters = initialize_pair_forecasters_by_granularity("hour")
            
            # Vérifications du flux de données
            forecaster = forecasters[0]
            assert forecaster.df_historical_data is not None
            assert forecaster.ts_historical_data == mock_ts
            
            # Vérifications des appels
            mock_get_data.assert_called_once_with(forecaster)
            mock_transform.assert_called_once()

    @patch('src.C9_data.send_data.save_forecasts_to_db')
    @patch('src.C9_model.save_model.save_forecasters_models')
    def test_pipeline_with_persistence(self, mock_save_models, mock_save_forecasts,
                                     mock_settings, mock_trading_pair_forecaster):
        """Test du pipeline avec persistance des modèles et prévisions"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        from src.C9_data.send_data import save_forecasts_to_db
        from src.C9_model.save_model import save_forecasters_models
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        
        with patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster'), \
             patch('src.C9_model.initiate_forecaster.time_series_transformation_steps'):
            
            # Initialisation
            forecasters = initialize_pair_forecasters_by_granularity("hour")
            
            # Simulation de la sauvegarde
            save_forecasts_to_db(forecasters)
            save_forecasters_models(forecasters, "hour")
            
            # Vérifications
            mock_save_forecasts.assert_called_once_with(forecasters)
            mock_save_models.assert_called_once_with(forecasters, "hour")

    def test_pipeline_error_recovery(self, mock_settings, mock_trading_pair_forecaster):
        """Test de récupération d'erreurs dans le pipeline"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        
        # Test avec erreur dans get_data
        with patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster') as mock_get_data:
            mock_get_data.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                initialize_pair_forecasters_by_granularity("hour")

    def test_pipeline_multiple_pairs(self, mock_settings, sample_ohlcv_data):
        """Test du pipeline avec plusieurs paires de trading"""
        # Configuration avec plusieurs paires
        with patch('src.C9_model.initiate_forecaster.HourModelsSettings') as mock_hour_settings:
            mock_hour_settings.pair_models = [
                {
                    "trading_pair_id": 1,
                    "symbol": "BTC-USD",
                    "granularity_type": "hour",
                    "freq": "h"
                },
                {
                    "trading_pair_id": 2,
                    "symbol": "ETH-USD",
                    "granularity_type": "hour",
                    "freq": "h"
                }
            ]
            
            with patch('src.C9_model.initiate_forecaster.TradingPairForecaster') as mock_class, \
                 patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster') as mock_get_data, \
                 patch('src.C9_model.initiate_forecaster.time_series_transformation_steps') as mock_transform:
                
                mock_get_data.return_value = sample_ohlcv_data
                mock_transform.return_value = Mock()
                
                from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
                forecasters = initialize_pair_forecasters_by_granularity("hour")
                
                # Vérifications
                assert len(forecasters) == 2
                assert mock_class.call_count == 2

    @patch('src.utils.functions.requests.post')
    @patch('src.C9_data.fetch_data.fetch_ohlcv')
    def test_pipeline_authentication_integration(self, mock_fetch, mock_post, mock_api_responses):
        """Test d'intégration avec l'authentification API"""
        from src.C9_data.fetch_data import get_data_for_pair_forecaster
        
        # Mock de la réponse d'authentification
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response
        
        # Mock de fetch_ohlcv
        mock_fetch.return_value = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5, freq='h'),
            'close': [50000, 51000, 52000, 51500, 52500]
        })
        
        # Mock forecaster
        mock_forecaster = Mock()
        mock_forecaster.trading_pair_id = 1
        mock_forecaster.granularity_type = "hourly"  # Utiliser "hourly" au lieu de "hour"
        
        # Test de récupération de données avec authentification
        result = get_data_for_pair_forecaster(mock_forecaster)
        
        # Vérifications
        assert result is not None
        mock_post.assert_called_once()  # Vérifier que l'authentification a été appelée
        mock_fetch.assert_called_once_with(1, "hourly", "test_token")

    def test_end_to_end_workflow(self, mock_settings, mock_trading_pair_forecaster, 
                                sample_ohlcv_data, mock_timeseries):
        """Test du workflow complet end-to-end"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        from src.C9_model.predict_model import make_forecasts
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        
        # Configuration des mocks pour le workflow complet
        with patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster') as mock_get_data, \
             patch('src.C9_model.initiate_forecaster.time_series_transformation_steps') as mock_transform, \
             patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model') as mock_train:
            
            # Configuration des mocks
            mock_get_data.return_value = sample_ohlcv_data
            mock_transform.return_value = mock_timeseries
            mock_get_last.return_value = None
            mock_instance.model_instance.predict.return_value = Mock()
            
            # 1. Initialisation
            forecasters = initialize_pair_forecasters_by_granularity("hour")
            
            # 2. Prédictions
            make_forecasts(forecasters)
            
            # 3. Vérifications du workflow complet
            assert len(forecasters) == 1
            forecaster = forecasters[0]
            
            # Vérifications des étapes
            mock_get_data.assert_called_once()
            mock_transform.assert_called_once()
            mock_train.assert_called_once()
            forecaster.model_instance.predict.assert_called_once()
            forecaster.add_forecast_to_df.assert_called_once()

    def test_pipeline_configuration_validation(self, mock_settings):
        """Test de validation de la configuration du pipeline"""
        mock_hour_settings, mock_day_settings = mock_settings
        
        # Vérification de la structure des configurations
        for pair_model in mock_hour_settings.pair_models:
            required_keys = ["trading_pair_id", "symbol", "granularity_type", "freq"]
            for key in required_keys:
                assert key in pair_model
            
            # Validation des types
            assert isinstance(pair_model["trading_pair_id"], int)
            assert isinstance(pair_model["symbol"], str)
            assert isinstance(pair_model["granularity_type"], str)
            assert isinstance(pair_model["freq"], str)
        
        # Test avec configuration invalide
        invalid_config = [{"incomplete": "config"}]
        mock_hour_settings.pair_models = invalid_config
        
        with patch('src.C9_model.initiate_forecaster.TradingPairForecaster') as mock_class:
            mock_class.side_effect = KeyError("Missing key")
            
            from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
            
            with pytest.raises(KeyError):
                initialize_pair_forecasters_by_granularity("hour")
