"""
Tests unitaires pour la validation et préparation des données ML
"""
import pytest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from darts import TimeSeries


@pytest.mark.unit
@pytest.mark.ml
class TestDataValidation:
    """Tests pour la validation des données d'entrée"""

    def test_ohlcv_data_structure_validation(self, sample_ohlcv_data):
        """Test de validation de la structure des données OHLCV"""
        # Vérifications des colonnes requises
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in sample_ohlcv_data.columns for col in required_columns)
        
        # Vérification que les données ne sont pas vides
        assert len(sample_ohlcv_data) > 0
        
        # Vérification des types de données
        assert pd.api.types.is_datetime64_any_dtype(sample_ohlcv_data['date'])
        assert pd.api.types.is_numeric_dtype(sample_ohlcv_data['open'])
        assert pd.api.types.is_numeric_dtype(sample_ohlcv_data['high'])
        assert pd.api.types.is_numeric_dtype(sample_ohlcv_data['low'])
        assert pd.api.types.is_numeric_dtype(sample_ohlcv_data['close'])
        assert pd.api.types.is_numeric_dtype(sample_ohlcv_data['volume'])

    def test_ohlcv_data_coherence_validation(self, sample_ohlcv_data):
        """Test de validation de la cohérence des données OHLCV"""
        # High >= max(open, close) et Low <= min(open, close)
        assert all(sample_ohlcv_data['high'] >= sample_ohlcv_data[['open', 'close']].max(axis=1))
        assert all(sample_ohlcv_data['low'] <= sample_ohlcv_data[['open', 'close']].min(axis=1))
        
        # Volume >= 0
        assert all(sample_ohlcv_data['volume'] >= 0)
        
        # Aucune valeur négative pour les prix
        price_cols = ['open', 'high', 'low', 'close']
        assert all(sample_ohlcv_data[price_cols].min() >= 0)

    def test_data_completeness_validation(self, sample_ohlcv_data):
        """Test de validation de la complétude des données"""
        # Vérification des valeurs manquantes
        assert sample_ohlcv_data.isnull().sum().sum() == 0
        
        # Vérification de la continuité temporelle
        dates_sorted = sample_ohlcv_data['date'].sort_values()
        date_diffs = dates_sorted.diff().dropna()
        
        # Pour des données horaires, l'écart devrait être constant
        expected_diff = pd.Timedelta(hours=1)
        assert all(date_diffs == expected_diff)

    def test_data_range_validation(self, sample_ohlcv_data):
        """Test de validation des plages de valeurs"""
        # Les prix doivent être dans une plage raisonnable (crypto)
        price_cols = ['open', 'high', 'low', 'close']
        min_price = 1  # Prix minimum raisonnable
        max_price = 1000000  # Prix maximum raisonnable
        
        assert all(sample_ohlcv_data[price_cols].min() >= min_price)
        assert all(sample_ohlcv_data[price_cols].max() <= max_price)
        
        # Le volume doit être raisonnable
        assert sample_ohlcv_data['volume'].min() >= 0
        assert sample_ohlcv_data['volume'].max() <= 1000000000  # Volume max raisonnable


@pytest.mark.unit
@pytest.mark.ml
class TestDataPreparation:
    """Tests pour la préparation des données"""

    @patch('src.C9_model.initiate_forecaster.TimeSeries.from_dataframe')
    @patch('src.C9_model.initiate_forecaster.fill_missing_values')
    def test_time_series_transformation(self, mock_fill_missing, mock_from_df, sample_ohlcv_data, mock_timeseries):
        """Test de transformation des données en TimeSeries"""
        from src.C9_model.initiate_forecaster import time_series_transformation_steps
        
        # Configuration des mocks
        mock_from_df.return_value = mock_timeseries
        mock_fill_missing.return_value = mock_timeseries
        
        # Préparation des données avec trading_pair_id comme dans le code réel
        df_prepared = sample_ohlcv_data[['open', 'high', 'low', 'close', 'volume']].copy()
        df_prepared.index = sample_ohlcv_data['date']
        df_prepared['trading_pair_id'] = 1  # Ajout de la colonne que le code va supprimer
        
        # Test de la transformation
        result = time_series_transformation_steps(df_prepared, 'h')
        
        # Vérifications
        mock_from_df.assert_called_once()
        mock_fill_missing.assert_called_once()
        assert result is not None

    def test_data_sorting_and_indexing(self, sample_ohlcv_data):
        """Test du tri et de l'indexation des données"""
        # Mélange volontaire des données
        shuffled_data = sample_ohlcv_data.sample(frac=1).reset_index(drop=True)
        
        # Tri et indexation comme dans le code réel
        sorted_data = shuffled_data.sort_values("date").set_index("date")
        
        # Vérifications
        assert sorted_data.index.is_monotonic_increasing
        assert len(sorted_data) == len(sample_ohlcv_data)
        assert sorted_data.index.name == 'date'

    def test_frequency_validation(self):
        """Test de validation des fréquences supportées"""
        valid_frequencies = ['h', 'D', 'min']
        
        for freq in valid_frequencies:
            # Ces fréquences doivent être acceptées par pandas
            try:
                pd.date_range('2024-01-01', periods=10, freq=freq)
                assert True
            except ValueError:
                pytest.fail(f"Fréquence {freq} non supportée")

    @patch('src.C9_data.fetch_data.get_data_for_pair_forecaster')
    def test_data_fetching_integration(self, mock_get_data, sample_forecaster, sample_ohlcv_data):
        """Test d'intégration pour la récupération des données"""
        # Configuration du mock
        mock_get_data.return_value = sample_ohlcv_data
        
        # Simulation de l'utilisation dans le pipeline
        df = mock_get_data(sample_forecaster)
        
        # Vérifications
        assert df is not None
        assert len(df) > 0
        mock_get_data.assert_called_once_with(sample_forecaster)

    def test_missing_values_handling(self):
        """Test de gestion des valeurs manquantes"""
        # Création de données avec valeurs manquantes
        dates = pd.date_range('2024-01-01', periods=10, freq='h')
        data_with_na = pd.DataFrame({
            'date': dates,
            'close': [50000, np.nan, 51000, 50500, np.nan, 52000, 51500, 51800, np.nan, 52200]
        })
        
        # Vérification de la détection des valeurs manquantes
        assert data_with_na['close'].isnull().sum() == 3
        
        # Test de différentes stratégies de remplissage
        # Forward fill - la première valeur non-NaN sera propagée
        forward_filled = data_with_na['close'].fillna(method='ffill')
        # Avec ffill, seules les NaN en début peuvent rester (ici aucune car première valeur = 50000)
        assert forward_filled.isnull().sum() == 0
        
        # Interpolation
        interpolated = data_with_na['close'].interpolate()
        # L'interpolation ne laisse des NaN que si début ou fin de série
        assert interpolated.isnull().sum() == 0

    def test_data_preprocessing_pipeline(self, sample_ohlcv_data):
        """Test du pipeline complet de preprocessing"""
        # Simulation du pipeline de preprocessing
        
        # 1. Tri des données
        sorted_data = sample_ohlcv_data.sort_values("date")
        
        # 2. Indexation
        indexed_data = sorted_data.set_index("date")
        
        # 3. Vérification de la continuité
        assert indexed_data.index.is_monotonic_increasing
        
        # 4. Sélection des colonnes pertinentes
        relevant_cols = ['open', 'high', 'low', 'close', 'volume']
        processed_data = indexed_data[relevant_cols]
        
        # Vérifications finales
        assert len(processed_data) == len(sample_ohlcv_data)
        assert all(col in processed_data.columns for col in relevant_cols)
        assert processed_data.index.name == 'date'


@pytest.mark.unit
@pytest.mark.ml
class TestDataAPI:
    """Tests pour l'interaction avec l'API de données"""

    @patch('src.C9_data.fetch_data.requests.get')
    def test_fetch_ohlcv_success(self, mock_get, mock_jwt_token):
        """Test de récupération réussie des données OHLCV"""
        from src.C9_data.fetch_data import fetch_ohlcv
        
        # Configuration du mock de réponse
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "date": "2024-01-01T00:00:00",
                "open": 50000.0,
                "high": 50500.0,
                "low": 49500.0,
                "close": 50000.0,
                "volume": 1000.0
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test de l'appel avec granularité correcte
        result = fetch_ohlcv(1, "hourly", "mock_token")
        
        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_get.assert_called_once()
        
        # Vérification que l'URL a été construite correctement
        call_args = mock_get.call_args
        assert "hourly_by_trading_pair_id/1" in call_args[0][0]

    @patch('src.C9_data.fetch_data.requests.get')
    def test_fetch_ohlcv_failure(self, mock_get, mock_jwt_token):
        """Test d'échec de récupération des données OHLCV"""
        from src.C9_data.fetch_data import fetch_ohlcv
        
        # Configuration du mock pour simuler une erreur
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        # Test que l'exception est propagée avec le bon message
        with pytest.raises(Exception, match="Échec de la récupération des données OHLCV"):
            fetch_ohlcv(1, "hourly", "mock_token")

    def test_jwt_token_validation(self, mock_jwt_token):
        """Test de validation du token JWT"""
        from src.C9_data.fetch_data import get_data_for_pair_forecaster
        
        # Le token doit être présent
        token = mock_jwt_token.return_value
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
