"""
Tests unitaires pour les prédictions des modèles ML
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from darts import TimeSeries


@pytest.mark.unit
@pytest.mark.ml
class TestModelPrediction:
    """Tests pour les prédictions des modèles"""

    @patch('src.C9_model.predict_model.train_model')
    @patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster')
    def test_make_forecasts_no_previous_forecast(self, mock_get_last, mock_train, sample_forecaster):
        """Test de prédiction quand aucune prévision précédente n'existe"""
        from src.C9_model.predict_model import make_forecasts
        
        # Configuration - aucune prévision précédente
        mock_get_last.return_value = None
        
        # Configuration du forecaster
        sample_forecaster.df_historical_data = pd.DataFrame(
            index=pd.date_range('2024-01-01', periods=10, freq='h')
        )
        sample_forecaster.freq = 'h'
        
        # Mock du modèle
        mock_forecast = Mock()
        sample_forecaster.model_instance.predict.return_value = mock_forecast
        
        # Test
        make_forecasts([sample_forecaster])
        
        # Vérifications
        mock_train.assert_called_once()
        sample_forecaster.model_instance.predict.assert_called_once_with(1)
        sample_forecaster.add_forecast_to_df.assert_called_once_with(mock_forecast, "current_forecast")

    @patch('src.C9_model.predict_model.train_model')
    @patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster')
    def test_make_forecasts_with_previous_forecast(self, mock_get_last, mock_train, sample_forecaster):
        """Test de prédiction avec des prévisions précédentes"""
        from src.C9_model.predict_model import make_forecasts
        
        # Configuration - prévision précédente existe
        last_forecast = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-01 05:00:00')]
        })
        mock_get_last.return_value = last_forecast
        
        # Configuration du forecaster avec données historiques plus récentes
        sample_forecaster.df_historical_data = pd.DataFrame(
            index=pd.date_range('2024-01-01', periods=10, freq='h')
        )
        sample_forecaster.freq = 'h'
        
        # Mock du modèle
        mock_forecast = Mock()
        sample_forecaster.model_instance.predict.return_value = mock_forecast
        
        # Test
        make_forecasts([sample_forecaster])
        
        # Vérifications - doit faire plusieurs prédictions pour rattraper
        assert mock_train.call_count >= 1
        assert sample_forecaster.model_instance.predict.call_count >= 1

    def test_make_forecast_basic(self, mock_darts_model):
        """Test de base pour make_forecast"""
        from src.C9_model.predict_model import make_forecast
        
        freq = 'h'
        start = pd.Timestamp('2024-01-01')
        end = pd.Timestamp('2024-01-01 02:00:00')
        
        # Mock de la prédiction
        mock_forecast = Mock()
        mock_darts_model.predict.return_value = mock_forecast
        
        # Test
        result = make_forecast(mock_darts_model, freq, start, end)
        
        # Vérifications
        assert result == mock_forecast
        # Doit prédire 3 périodes (0h, 1h, 2h)
        mock_darts_model.predict.assert_called_once_with(3)

    def test_make_forecast_date_range_calculation(self, mock_darts_model):
        """Test du calcul correct de la plage de dates"""
        from src.C9_model.predict_model import make_forecast
        
        test_cases = [
            ('h', '2024-01-01 00:00:00', '2024-01-01 05:00:00', 6),  # 6 heures
            ('D', '2024-01-01', '2024-01-07', 7),  # 7 jours
            ('min', '2024-01-01 00:00:00', '2024-01-01 00:10:00', 11),  # 11 minutes
        ]
        
        for freq, start_str, end_str, expected_periods in test_cases:
            mock_darts_model.reset_mock()
            
            start = pd.Timestamp(start_str)
            end = pd.Timestamp(end_str)
            
            make_forecast(mock_darts_model, freq, start, end)
            
            mock_darts_model.predict.assert_called_once_with(expected_periods)

    def test_make_forecast_uses_date_range(self, mock_darts_model):
        """Test que make_forecast utilise correctement pd.date_range pour calculer les périodes"""
        from src.C9_model.predict_model import make_forecast
        
        freq = 'h'
        start = pd.Timestamp('2024-01-01')
        end = pd.Timestamp('2024-01-01 04:00:00')
        
        # Test - vérifions le comportement attendu
        make_forecast(mock_darts_model, freq, start, end)
        
        # Vérifications - le modèle doit être appelé avec le bon nombre de périodes
        # Entre '2024-01-01' et '2024-01-01 04:00:00' avec freq='h', il y a 5 périodes
        expected_periods = len(pd.date_range(start, end, freq=freq))
        assert expected_periods == 5
        mock_darts_model.predict.assert_called_once_with(5)

    def test_forecast_data_continuity(self, sample_forecaster):
        """Test de la continuité des données de prévision"""
        from src.C9_model.predict_model import make_forecasts
        
        # Configuration du forecaster avec des données continues
        dates = pd.date_range('2024-01-01', periods=24, freq='h')
        sample_forecaster.df_historical_data = pd.DataFrame(index=dates)
        sample_forecaster.freq = 'h'
        
        with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model') as mock_train:
            
            mock_get_last.return_value = None
            mock_forecast = Mock()
            sample_forecaster.model_instance.predict.return_value = mock_forecast
            
            # Test
            make_forecasts([sample_forecaster])
            
            # Vérification que la prédiction est ajoutée
            sample_forecaster.add_forecast_to_df.assert_called_with(mock_forecast, "current_forecast")

    def test_multiple_forecasters(self):
        """Test avec plusieurs forecasters"""
        from src.C9_model.predict_model import make_forecasts
        
        # Création de plusieurs forecasters
        forecasters = []
        for i in range(3):
            forecaster = Mock()
            forecaster.df_historical_data = pd.DataFrame(
                index=pd.date_range(f'2024-01-0{i+1}', periods=10, freq='h')
            )
            forecaster.freq = 'h'
            forecaster.model_instance.predict.return_value = Mock()
            forecasters.append(forecaster)
        
        with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model'):
            
            mock_get_last.return_value = None
            
            # Test
            make_forecasts(forecasters)
            
            # Vérifications - chaque forecaster doit être traité
            for forecaster in forecasters:
                forecaster.model_instance.predict.assert_called_once()
                forecaster.add_forecast_to_df.assert_called_once()

    @patch('src.C9_model.predict_model.train_model')
    @patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster')
    def test_forecast_error_handling(self, mock_get_last, mock_train, sample_forecaster):
        """Test de gestion d'erreurs pendant la prédiction"""
        from src.C9_model.predict_model import make_forecasts
        
        mock_get_last.return_value = None
        sample_forecaster.df_historical_data = pd.DataFrame(
            index=pd.date_range('2024-01-01', periods=10, freq='h')
        )
        sample_forecaster.freq = 'h'
        
        # Configuration du modèle pour lever une exception
        sample_forecaster.model_instance.predict.side_effect = ValueError("Prediction failed")
        
        # Test que l'exception est propagée
        with pytest.raises(ValueError, match="Prediction failed"):
            make_forecasts([sample_forecaster])

    def test_timedelta_operations(self, sample_forecaster):
        """Test des opérations de Timedelta"""
        from src.C9_model.predict_model import make_forecasts
        
        # Test avec différentes fréquences
        frequencies = ['h', 'D', 'min']
        
        for freq in frequencies:
            sample_forecaster.freq = freq
            sample_forecaster.df_historical_data = pd.DataFrame(
                index=pd.date_range('2024-01-01', periods=5, freq=freq)
            )
            
            with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
                 patch('src.C9_model.predict_model.train_model'):
                
                mock_get_last.return_value = None
                sample_forecaster.model_instance.predict.return_value = Mock()
                
                # Test - ne doit pas lever d'exception pour les opérations Timedelta
                try:
                    make_forecasts([sample_forecaster])
                    assert True
                except Exception as e:
                    pytest.fail(f"Erreur avec fréquence {freq}: {e}")


@pytest.mark.unit
@pytest.mark.ml  
class TestForecastDataHandling:
    """Tests pour la gestion des données de prévision"""

    def test_forecast_data_structure(self, sample_forecast_data):
        """Test de la structure des données de prévision"""
        # Vérification des colonnes nécessaires
        required_columns = ['forecast', 'date']
        for col in required_columns:
            assert col in sample_forecast_data.columns
        
        # Vérification des types
        assert pd.api.types.is_numeric_dtype(sample_forecast_data['forecast'])
        assert pd.api.types.is_datetime64_any_dtype(sample_forecast_data['date'])

    def test_forecast_value_validation(self, sample_forecast_data):
        """Test de validation des valeurs de prévision"""
        # Les prévisions doivent être positives (prix crypto)
        assert all(sample_forecast_data['forecast'] > 0)
        
        # Les prévisions doivent être dans une plage raisonnable
        assert all(sample_forecast_data['forecast'] < 1000000)  # Max raisonnable
        assert all(sample_forecast_data['forecast'] > 1)       # Min raisonnable

    def test_forecast_date_continuity(self):
        """Test de la continuité des dates de prévision"""
        # Création de données avec dates continues
        dates = pd.date_range('2024-01-01', periods=5, freq='h')
        forecasts = [50000 + i*100 for i in range(5)]
        
        df = pd.DataFrame({'date': dates, 'forecast': forecasts})
        
        # Vérification de la continuité
        date_diffs = df['date'].diff().dropna()
        expected_diff = pd.Timedelta(hours=1)
        assert all(date_diffs == expected_diff)

    def test_forecast_trend_analysis(self, sample_forecast_data):
        """Test d'analyse de tendance des prévisions"""
        # Calcul des variations
        forecast_values = sample_forecast_data['forecast'].values
        variations = np.diff(forecast_values)
        
        # Les variations doivent être raisonnables (pas de changements extrêmes)
        max_variation_percent = 0.1  # 10% max entre deux périodes consécutives
        for i, variation in enumerate(variations):
            percent_change = abs(variation) / forecast_values[i]
            assert percent_change <= max_variation_percent, f"Variation trop importante: {percent_change:.2%}"

    def test_forecast_aggregation(self):
        """Test d'agrégation des prévisions"""
        # Simulation de prévisions multiples
        forecasts_data = [
            pd.DataFrame({
                'forecast': [50000, 51000],
                'date': pd.date_range('2024-01-01', periods=2, freq='h')
            }),
            pd.DataFrame({
                'forecast': [52000, 53000],
                'date': pd.date_range('2024-01-01 02:00:00', periods=2, freq='h')
            })
        ]
        
        # Agrégation
        combined = pd.concat(forecasts_data, ignore_index=True)
        
        # Vérifications
        assert len(combined) == 4
        assert combined['forecast'].is_monotonic_increasing  # Dans cet exemple
        assert combined['date'].is_monotonic_increasing

    def test_forecast_persistence(self, sample_forecaster):
        """Test de persistance des prévisions"""
        from src.C9_model.predict_model import make_forecasts
        
        # Configuration
        sample_forecaster.df_historical_data = pd.DataFrame(
            index=pd.date_range('2024-01-01', periods=5, freq='h')
        )
        
        forecast_calls = []
        
        def mock_add_forecast(forecast, forecast_type):
            forecast_calls.append((forecast, forecast_type))
        
        sample_forecaster.add_forecast_to_df.side_effect = mock_add_forecast
        
        with patch('src.C9_model.predict_model.get_last_forecast_for_pair_forecaster') as mock_get_last, \
             patch('src.C9_model.predict_model.train_model'):
            
            mock_get_last.return_value = None
            mock_forecast = Mock()
            sample_forecaster.model_instance.predict.return_value = mock_forecast
            
            # Test
            make_forecasts([sample_forecaster])
            
            # Vérifications
            assert len(forecast_calls) == 1
            assert forecast_calls[0][0] == mock_forecast
            assert forecast_calls[0][1] == "current_forecast"
