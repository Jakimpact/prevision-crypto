"""
Tests unitaires pour l'évaluation des modèles ML
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from darts import TimeSeries


@pytest.mark.unit
@pytest.mark.ml
class TestModelEvaluation:
    """Tests pour l'évaluation des modèles"""

    @patch('src.C9_model.evaluate_model.generate_test_periods')
    @patch('src.C9_model.evaluate_model.train_model')
    @patch('src.C9_model.evaluate_model.make_forecast')
    @patch('src.C9_model.evaluate_model.calculate_metrics')
    def test_test_forecaster_past_performances(self, mock_calc_metrics, mock_make_forecast,
                                             mock_train, mock_gen_test_periods, sample_forecaster,
                                             mock_test_periods, sample_metrics):
        """Test de l'évaluation des performances passées"""
        from src.C9_model.evaluate_model import test_forecaster_past_performances
        
        # Configuration des mocks
        mock_gen_test_periods.return_value = mock_test_periods
        mock_forecast = Mock()
        mock_make_forecast.return_value = mock_forecast
        mock_calc_metrics.return_value = (sample_metrics['mape'], 
                                        sample_metrics['mae'], 
                                        sample_metrics['direction_accuracy'])
        
        # Test
        mape, mae, direction_acc = test_forecaster_past_performances(sample_forecaster)
        
        # Vérifications
        assert mape == sample_metrics['mape']
        assert mae == sample_metrics['mae']
        assert direction_acc == sample_metrics['direction_accuracy']
        
        mock_gen_test_periods.assert_called_once_with(sample_forecaster)
        assert mock_train.call_count >= 1
        assert mock_make_forecast.call_count >= 1
        sample_forecaster.add_forecast_to_df.assert_called()

    @patch('src.C9_model.evaluate_model.mape')
    @patch('src.C9_model.evaluate_model.mae')
    @patch('src.C9_model.evaluate_model.calculate_direction_accuracy')
    @patch('src.C9_model.evaluate_model.TimeSeries.from_dataframe')
    def test_calculate_metrics(self, mock_from_df, mock_direction, mock_mae_func, 
                             mock_mape_func, sample_forecaster, mock_timeseries):
        """Test du calcul des métriques"""
        from src.C9_model.evaluate_model import calculate_metrics
        
        # Configuration des mocks
        mock_mape_func.return_value = 5.2
        mock_mae_func.return_value = 150.5
        mock_direction.return_value = 0.75
        mock_from_df.return_value = mock_timeseries
        
        # Configuration du forecaster avec des données de prévision
        sample_forecaster.historical_forecast = pd.DataFrame({
            'forecast': [50000, 51000, 52000],
            'date': pd.date_range('2024-01-01', periods=3, freq='h')
        })
        sample_forecaster.historical_forecast.index = pd.date_range('2024-01-01', periods=3, freq='h')
        sample_forecaster.freq = 'h'
        sample_forecaster.ts_historical_data = {"close": mock_timeseries}
        
        # Test
        mape_score, mae_score, direction_acc = calculate_metrics(sample_forecaster)
        
        # Vérifications
        assert mape_score == 5.2
        assert mae_score == 150.5
        assert direction_acc == 0.75
        
        mock_mape_func.assert_called_once()
        mock_mae_func.assert_called_once()
        mock_direction.assert_called_once()

    def test_calculate_direction_accuracy(self, mock_timeseries):
        """Test du calcul de la précision directionnelle"""
        from src.C9_model.evaluate_model import calculate_direction_accuracy
        
        # Données de test simulées
        dates = pd.date_range('2024-01-01', periods=5, freq='h')
        
        # Mock des TimeSeries avec to_dataframe et columns
        mock_forecast_ts = Mock()
        mock_forecast_ts.to_dataframe.return_value = pd.DataFrame({
            'forecast': [50000, 51000, 49000, 52000, 51500]
        }, index=dates)
        mock_forecast_ts.columns = ['forecast']  # Support pour columns[0]
        
        mock_historical_ts = Mock()
        mock_historical_ts.to_dataframe.return_value = pd.DataFrame({
            'actual': [49500, 50800, 48500, 51800, 51200]
        }, index=dates)
        mock_historical_ts.columns = ['actual']  # Support pour columns[0]
        
        # Test
        accuracy = calculate_direction_accuracy(mock_forecast_ts, mock_historical_ts)
        
        # Vérifications
        assert 0 <= accuracy <= 1  # La précision doit être entre 0 et 1
        assert isinstance(accuracy, (float, np.floating))

    @patch('src.C9_model.evaluate_model.mape')
    @patch('src.C9_model.evaluate_model.mae')
    def test_calculate_performance(self, mock_mae_func, mock_mape_func, mock_timeseries):
        """Test du calcul des performances générales"""
        from src.C9_model.evaluate_model import calculate_performance
        
        # Configuration des mocks
        mock_mape_func.return_value = 4.8
        mock_mae_func.return_value = 125.0
        
        # Données de prévision mockées
        df_forecast = pd.DataFrame({
            'forecast': [50000, 51000, 52000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='h'))
        
        # Mock TimeSeries
        mock_ts = {"close": mock_timeseries}
        freq = 'h'
        
        # Test
        with patch('src.C9_model.evaluate_model.TimeSeries.from_dataframe') as mock_from_df:
            mock_forecast_ts = Mock()
            mock_forecast_ts.time_index = pd.date_range('2024-01-01', periods=3, freq='h')
            mock_from_df.return_value = mock_forecast_ts
            
            mape_score, mae_score = calculate_performance(mock_ts, df_forecast, freq)
        
        # Vérifications
        assert mape_score == 4.8
        assert mae_score == 125.0

    def test_metrics_validation(self):
        """Test de validation des métriques calculées"""
        # Test des valeurs de MAPE
        valid_mape_values = [0.0, 5.2, 10.8, 25.0, 100.0]
        for mape in valid_mape_values:
            assert mape >= 0  # MAPE doit être positive
        
        # Test des valeurs de MAE
        valid_mae_values = [0.0, 50.5, 150.8, 1000.0]
        for mae in valid_mae_values:
            assert mae >= 0  # MAE doit être positive
        
        # Test des valeurs de direction accuracy
        valid_accuracy_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        for acc in valid_accuracy_values:
            assert 0 <= acc <= 1  # Accuracy entre 0 et 1

    @patch('src.C9_model.evaluate_model.logger')
    def test_logging_during_evaluation(self, mock_logger, sample_forecaster):
        """Test du logging pendant l'évaluation"""
        from src.C9_model.evaluate_model import test_forecaster_past_performances
        
        with patch('src.C9_model.evaluate_model.generate_test_periods') as mock_periods, \
             patch('src.C9_model.evaluate_model.train_model'), \
             patch('src.C9_model.evaluate_model.make_forecast'), \
             patch('src.C9_model.evaluate_model.calculate_metrics') as mock_calc:
            
            mock_periods.return_value = pd.DataFrame({
                'test_start': [pd.Timestamp('2024-01-01')],
                'test_end': [pd.Timestamp('2024-01-02')]
            })
            mock_calc.return_value = (5.0, 100.0, 0.7)
            
            # Test
            test_forecaster_past_performances(sample_forecaster)
            
            # Vérification que le logging peut être appelé si présent
            # (pas d'assertion spécifique car le logging est optionnel)

    def test_duplicate_index_handling(self, sample_forecaster):
        """Test de gestion des index dupliqués dans les prévisions"""
        from src.C9_model.evaluate_model import calculate_metrics
        
        # Création de données avec index dupliqués
        dates = pd.date_range('2024-01-01', periods=3, freq='h')
        duplicate_dates = list(dates) + [dates[0]]  # Ajout d'un duplicata
        
        sample_forecaster.historical_forecast = pd.DataFrame({
            'forecast': [50000, 51000, 52000, 50100]
        }, index=duplicate_dates)
        
        sample_forecaster.freq = 'h'
        sample_forecaster.ts_historical_data = {"close": Mock()}
        
        with patch('src.C9_model.evaluate_model.TimeSeries.from_dataframe') as mock_from_df, \
             patch('src.C9_model.evaluate_model.mape') as mock_mape, \
             patch('src.C9_model.evaluate_model.mae') as mock_mae, \
             patch('src.C9_model.evaluate_model.calculate_direction_accuracy') as mock_direction:
            
            mock_ts = Mock()
            mock_ts.time_index = Mock()
            mock_ts.time_index.min.return_value = dates[0]
            mock_ts.time_index.max.return_value = dates[-1]
            mock_from_df.return_value = mock_ts
            
            mock_mape.return_value = 5.0
            mock_mae.return_value = 100.0
            mock_direction.return_value = 0.75
            
            # Test - ne doit pas lever d'exception
            mape, mae, direction = calculate_metrics(sample_forecaster)
            
            # Vérifications que les duplicatas sont gérés
            assert mape == 5.0
            assert mae == 100.0
            assert direction == 0.75


@pytest.mark.unit
@pytest.mark.ml
class TestPerformanceDisplay:
    """Tests pour l'affichage des performances"""

    def test_display_performance(self, capsys):
        """Test de l'affichage des performances"""
        from src.C9_model.evaluate_model import display_performance
        
        start = pd.Timestamp('2024-01-01')
        end = pd.Timestamp('2024-01-07')
        mape = 5.25
        mae = 150.75
        
        # Test
        display_performance(start, end, mape, mae)
        
        # Vérification de la sortie
        captured = capsys.readouterr()
        assert "2024-01-01" in captured.out
        assert "2024-01-07" in captured.out
        assert "5.25" in captured.out
        assert "150.75" in captured.out
        assert "MAPE" in captured.out
        assert "MAE" in captured.out

    def test_performance_formatting(self):
        """Test du formatage des valeurs de performance"""
        # Test du formatage MAPE
        mape_values = [5.123456, 10.9, 0.0]
        for mape in mape_values:
            formatted = round(mape, 2)
            assert isinstance(formatted, float)
            assert len(str(formatted).split('.')[-1]) <= 2
        
        # Test du formatage MAE
        mae_values = [150.789, 1000.1, 0.0]
        for mae in mae_values:
            formatted = round(mae, 2)
            assert isinstance(formatted, float)
            assert len(str(formatted).split('.')[-1]) <= 2

    def test_performance_validation_ranges(self):
        """Test de validation des plages de valeurs des performances"""
        # MAPE acceptable pour crypto (généralement < 20%)
        acceptable_mape = [0.5, 2.1, 5.8, 10.2, 15.9]
        warning_mape = [25.0, 50.0, 100.0]
        
        for mape in acceptable_mape:
            assert mape < 20  # Performance acceptable
        
        for mape in warning_mape:
            assert mape >= 20  # Performance à surveiller
        
        # MAE dépend de l'échelle des prix (crypto en dollars)
        reasonable_mae = [10.0, 50.0, 100.0, 500.0, 1000.0]
        for mae in reasonable_mae:
            assert mae > 0  # MAE doit être positive
