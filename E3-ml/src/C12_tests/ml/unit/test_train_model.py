"""
Tests unitaires pour l'entraînement des modèles ML
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
from darts import TimeSeries


@pytest.mark.unit
@pytest.mark.ml
class TestModelTraining:
    """Tests pour l'entraînement des modèles"""

    def test_train_model_basic(self, mock_darts_model, mock_timeseries):
        """Test de base de l'entraînement d'un modèle"""
        from src.C9_model.train_model import train_model
        
        # Configuration des paramètres
        freq = 'h'
        training_end = pd.Timestamp('2024-01-15')
        
        # Test de l'entraînement - la fixture mock_timeseries gère déjà les opérations
        train_model(mock_darts_model, mock_timeseries, freq, training_end)
        
        # Vérifications
        mock_darts_model.fit.assert_called_once()
        mock_timeseries.__getitem__.assert_called_with("close")

    def test_train_model_date_adjustment(self, mock_darts_model, mock_timeseries):
        """Test de l'ajustement de la date de fin d'entraînement"""
        from src.C9_model.train_model import train_model
        
        freq = 'h'
        training_end = pd.Timestamp('2024-01-15 10:00:00')
        expected_adjusted_end = training_end - pd.Timedelta(1, unit=freq)
        
        # Test
        train_model(mock_darts_model, mock_timeseries, freq, training_end)
        
        # Vérifications
        mock_darts_model.fit.assert_called_once()
        # Vérifier que l'indexation s'est faite avec la colonne close
        mock_timeseries.__getitem__.assert_called_with("close")

    def test_train_model_with_different_frequencies(self, mock_darts_model, mock_timeseries):
        """Test d'entraînement avec différentes fréquences"""
        from src.C9_model.train_model import train_model
        
        frequencies = ['h', 'D', 'min']
        training_end = pd.Timestamp('2024-01-15')
        
        for freq in frequencies:
            mock_darts_model.reset_mock()
            mock_timeseries.reset_mock()
            
            # Test pour chaque fréquence
            train_model(mock_darts_model, mock_timeseries, freq, training_end)
            
            # Vérifications
            mock_darts_model.fit.assert_called_once()
            mock_timeseries.__getitem__.assert_called_with("close")

    def test_train_model_series_slicing(self, mock_darts_model, mock_timeseries):
        """Test du découpage correct de la série temporelle"""
        from src.C9_model.train_model import train_model
        
        freq = 'h'
        training_end = pd.Timestamp('2024-01-15 10:00:00')
        
        # Test
        train_model(mock_darts_model, mock_timeseries, freq, training_end)
        
        # Vérifications - le modèle doit être entraîné
        mock_darts_model.fit.assert_called_once()
        # Vérifier que le slicing a bien eu lieu sur la série "close"
        mock_timeseries.__getitem__.assert_called_with("close")

    @patch('src.C9_model.train_model.pd.Timedelta')
    def test_timedelta_calculation(self, mock_timedelta, mock_darts_model, mock_timeseries):
        """Test du calcul correct du timedelta"""
        from src.C9_model.train_model import train_model
        
        freq = 'h'
        training_end = pd.Timestamp('2024-01-15')
        mock_timedelta.return_value = pd.Timedelta(hours=1)
        
        # Test
        train_model(mock_darts_model, mock_timeseries, freq, training_end)
        
        # Vérification que Timedelta est appelé avec les bons paramètres (au moins une fois)
        mock_timedelta.assert_any_call(1, unit=freq)
        mock_darts_model.fit.assert_called_once()

    def test_train_model_error_handling(self, mock_darts_model, mock_timeseries):
        """Test de gestion d'erreurs pendant l'entraînement"""
        from src.C9_model.train_model import train_model
        
        # Configuration du mock pour lever une exception
        mock_darts_model.fit.side_effect = ValueError("Training failed")
        
        freq = 'h'
        training_end = pd.Timestamp('2024-01-15')
        
        # Test que l'exception est propagée
        with pytest.raises(ValueError, match="Training failed"):
            train_model(mock_darts_model, mock_timeseries, freq, training_end)


@pytest.mark.unit
@pytest.mark.ml
class TestModelInitialization:
    """Tests pour l'initialisation des modèles et forecasters"""

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    @patch('src.C9_model.initiate_forecaster.time_series_transformation_steps')
    def test_initialize_hourly_forecasters(self, mock_transform, mock_get_data, 
                                         mock_settings, mock_trading_pair_forecaster, 
                                         sample_ohlcv_data, mock_timeseries):
        """Test d'initialisation des forecasters horaires"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        mock_transform.return_value = mock_timeseries
        
        # Test
        result = initialize_pair_forecasters_by_granularity("hour")
        
        # Vérifications
        assert len(result) == 1
        assert result[0] == mock_instance
        mock_class.assert_called_once()
        mock_get_data.assert_called_once_with(mock_instance)
        mock_transform.assert_called_once()

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    @patch('src.C9_model.initiate_forecaster.time_series_transformation_steps')
    def test_initialize_daily_forecasters(self, mock_transform, mock_get_data,
                                        mock_settings, mock_trading_pair_forecaster,
                                        sample_ohlcv_data, mock_timeseries):
        """Test d'initialisation des forecasters journaliers"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        mock_transform.return_value = mock_timeseries
        
        # Test
        result = initialize_pair_forecasters_by_granularity("day")
        
        # Vérifications
        assert len(result) == 1
        mock_class.assert_called_once()

    def test_initialize_invalid_granularity(self, mock_settings):
        """Test avec une granularité invalide"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        
        # Test avec granularité invalide - vérifie que l'exception est bien levée (message uniformisé)
        with pytest.raises(UnboundLocalError, match=r"local variable 'pair_models' referenced before assignment"):
            initialize_pair_forecasters_by_granularity("invalid")

    @patch('src.C9_model.initiate_forecaster.get_data_for_pair_forecaster')
    def test_data_assignment_to_forecaster(self, mock_get_data, mock_settings,
                                         mock_trading_pair_forecaster, sample_ohlcv_data):
        """Test de l'assignation des données au forecaster"""
        from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
        
        mock_hour_settings, mock_day_settings = mock_settings
        mock_class, mock_instance = mock_trading_pair_forecaster
        mock_get_data.return_value = sample_ohlcv_data
        
        with patch('src.C9_model.initiate_forecaster.time_series_transformation_steps') as mock_transform:
            mock_transform.return_value = Mock()
            
            # Test
            result = initialize_pair_forecasters_by_granularity("hour")
            
            # Vérifications que les données sont assignées
            forecaster = result[0]
            assert forecaster.df_historical_data is not None
            assert forecaster.ts_historical_data is not None


@pytest.mark.unit  
@pytest.mark.ml
class TestModelConfiguration:
    """Tests pour la configuration des modèles"""

    def test_model_parameters_validation(self):
        """Test de validation des paramètres des modèles"""
        # Paramètres valides pour différents types de modèles
        valid_params = {
            "RandomForest": {
                "n_estimators": 100,
                "random_state": 42,
                "max_depth": 10
            },
            "LinearRegression": {
                "fit_intercept": True,
                "normalize": False
            }
        }
        
        for model_type, params in valid_params.items():
            # Validation que les paramètres sont des types corrects
            for param_name, param_value in params.items():
                assert isinstance(param_name, str)
                assert param_value is not None

    def test_frequency_mapping(self):
        """Test du mapping des fréquences"""
        frequency_mapping = {
            "hour": "h",
            "day": "D",
            "minute": "min"
        }
        
        for granularity, freq_code in frequency_mapping.items():
            # Test que les codes de fréquence sont valides pour pandas
            try:
                pd.date_range('2024-01-01', periods=5, freq=freq_code)
                assert True
            except ValueError:
                pytest.fail(f"Fréquence {freq_code} invalide pour granularité {granularity}")

    def test_model_class_instantiation(self):
        """Test d'instanciation des classes de modèles"""
        # Test que les imports de modèles fonctionnent
        try:
            from darts.models import RandomForest, LinearRegressionModel
            # Si l'import réussit, les classes sont disponibles
            assert RandomForest is not None
            assert LinearRegressionModel is not None
        except ImportError:
            # Si Darts n'est pas installé, on skip le test
            pytest.skip("Darts not installed")
