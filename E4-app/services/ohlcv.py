"""
Service pour récupérer les données OHLCV et de prévisions depuis l'API E1
pour la visualisation graphique.
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from config import Config
from utils.auth import get_auth_headers


class OHLCVService:
    """Service pour récupérer les données de prix et de prévisions."""
    
    def __init__(self):
        self.config = Config()
        # Paires disponibles dans l'application
        self.available_pairs = {
            "BTC-USDT": {"base": "BTC", "quote": "USDT"},
            "ETH-USDT": {"base": "ETH", "quote": "USDT"}
        }
    
    def get_available_pairs(self) -> Dict[str, Dict[str, str]]:
        """
        Retourne les paires disponibles dans l'application.
        
        Returns:
            Dict: Paires disponibles avec leurs symboles base et quote
        """
        return self.available_pairs
    
    def get_trading_pair_by_symbols(self, base_symbol: str, quote_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une paire de trading par ses symboles.
        
        Args:
            base_symbol: Symbole de la devise de base (ex: BTC)
            quote_symbol: Symbole de la devise de cotation (ex: USDT)
            
        Returns:
            Dict ou None: Informations sur la paire de trading
        """
        try:
            headers = get_auth_headers()
            if not headers:
                return None
                
            response = requests.get(
                f"{self.config.ENDPOINTS_E1['trading_pair']}/{base_symbol}/{quote_symbol}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Paire {base_symbol}/{quote_symbol} non trouvée: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Erreur de connexion lors de la récupération de la paire: {e}")
            return None
    
    def get_ohlcv_data(
        self, 
        trading_pair_id: int, 
        granularity: str = "hourly", 
        start_date: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Récupère les données OHLCV pour une paire de trading.
        
        Args:
            trading_pair_id: ID de la paire de trading
            granularity: Granularité des données ("minute", "hourly", "daily")
            start_date: Date de début (format ISO) - optionnel
            days_back: Nombre de jours à récupérer si pas de start_date
            
        Returns:
            List[Dict]: Liste des données OHLCV
        """
        try:
            headers = get_auth_headers()
            if not headers:
                return []
            
            # Construire l'URL selon la granularité
            endpoint_key = f"ohlcv_{granularity}"
            if endpoint_key not in self.config.ENDPOINTS_E1:
                print(f"Granularité non supportée: {granularity}")
                return []
            
            url = f"{self.config.ENDPOINTS_E1[endpoint_key]}/{trading_pair_id}"
            
            # Paramètres de la requête
            params = {}
            if start_date:
                params['start_date'] = start_date
            else:
                # Calculer une date de début par défaut
                start_date_obj = datetime.now() - timedelta(days=days_back)
                params['start_date'] = start_date_obj.isoformat()
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            else:
                print(f"Erreur lors de la récupération des données OHLCV: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"Erreur de connexion lors de la récupération des données OHLCV: {e}")
            return []
    
    def get_forecast_data(
        self, 
        trading_pair_id: int, 
        granularity: str = "hourly",
        start_date: Optional[str] = None,
        days_forward: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Récupère les données de prévisions pour une paire de trading.
        
        Args:
            trading_pair_id: ID de la paire de trading
            granularity: Granularité des prévisions ("hourly", "daily")
            start_date: Date de début (format ISO) - optionnel
            days_forward: Nombre de jours de prévisions à récupérer
            
        Returns:
            List[Dict]: Liste des prévisions
        """
        try:
            headers = get_auth_headers()
            if not headers:
                return []
            
            # Construire l'URL selon la granularité
            endpoint_key = f"forecast_{granularity}"
            if endpoint_key not in self.config.ENDPOINTS_E1:
                print(f"Granularité non supportée: {granularity}")
                return []
            
            url = f"{self.config.ENDPOINTS_E1[endpoint_key]}/{trading_pair_id}"
            
            # Paramètres de la requête
            params = {}
            if start_date:
                params['start_date'] = start_date
            else:
                # Pour les prévisions, commencer à partir d'aujourd'hui
                params['start_date'] = datetime.now().isoformat()
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            else:
                print(f"Erreur lors de la récupération des prévisions: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"Erreur de connexion lors de la récupération des prévisions: {e}")
            return []
    
    def get_combined_data(
        self,
        base_symbol: str,
        quote_symbol: str,
        granularity: str = "hourly",
        historical_days: int = 30,
        forecast_days: int = 7
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Récupère les données historiques et de prévisions pour une paire de trading.
        
        Args:
            base_symbol: Symbole de la devise de base
            quote_symbol: Symbole de la devise de cotation
            granularity: Granularité des données
            historical_days: Nombre de jours historiques
            forecast_days: Nombre de jours de prévisions
            
        Returns:
            Tuple: (données_ohlcv, prévisions, info_paire)
        """
        # Récupérer les informations de la paire
        trading_pair = self.get_trading_pair_by_symbols(base_symbol, quote_symbol)
        if not trading_pair:
            return [], [], None
        
        trading_pair_id = trading_pair.get('id')
        if not trading_pair_id:
            return [], [], None
        
        # Récupérer les données historiques
        ohlcv_data = self.get_ohlcv_data(
            trading_pair_id=trading_pair_id,
            granularity=granularity,
            days_back=historical_days
        )
        
        # Récupérer les prévisions
        forecast_data = self.get_forecast_data(
            trading_pair_id=trading_pair_id,
            granularity=granularity,
            days_forward=forecast_days
        )
        
        return ohlcv_data, forecast_data, trading_pair
    
    def get_all_data(
        self,
        base_symbol: str,
        quote_symbol: str,
        granularity: str = "hourly"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Récupère toutes les données historiques et de prévisions disponibles pour une paire de trading.
        
        Args:
            base_symbol: Symbole de la devise de base
            quote_symbol: Symbole de la devise de cotation
            granularity: Granularité des données
            
        Returns:
            Tuple: (données_ohlcv, prévisions, info_paire)
        """
        # Récupérer les informations de la paire
        trading_pair = self.get_trading_pair_by_symbols(base_symbol, quote_symbol)
        if not trading_pair:
            return [], [], None
        
        trading_pair_id = trading_pair.get('id')
        if not trading_pair_id:
            return [], [], None
        
        # Récupérer toutes les données historiques (sans limite de date)
        ohlcv_data = self.get_all_ohlcv_data(
            trading_pair_id=trading_pair_id,
            granularity=granularity
        )
        
        # Récupérer toutes les prévisions disponibles
        forecast_data = self.get_all_forecast_data(
            trading_pair_id=trading_pair_id,
            granularity=granularity
        )
        
        return ohlcv_data, forecast_data, trading_pair
    
    def get_all_ohlcv_data(
        self, 
        trading_pair_id: int, 
        granularity: str = "hourly"
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les données OHLCV disponibles pour une paire de trading.
        
        Args:
            trading_pair_id: ID de la paire de trading
            granularity: Granularité des données ("hourly", "daily")
            
        Returns:
            List[Dict]: Liste des données OHLCV
        """
        try:
            headers = get_auth_headers()
            if not headers:
                return []
            
            # Construire l'URL selon la granularité
            endpoint_key = f"ohlcv_{granularity}"
            if endpoint_key not in self.config.ENDPOINTS_E1:
                print(f"Granularité non supportée: {granularity}")
                return []
            
            url = f"{self.config.ENDPOINTS_E1[endpoint_key]}/{trading_pair_id}"
            
            # Pas de paramètres de date pour récupérer tout l'historique
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            else:
                print(f"Erreur lors de la récupération des données OHLCV: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"Erreur de connexion lors de la récupération des données OHLCV: {e}")
            return []
    
    def get_all_forecast_data(
        self, 
        trading_pair_id: int, 
        granularity: str = "hourly"
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les données de prévisions disponibles pour une paire de trading.
        
        Args:
            trading_pair_id: ID de la paire de trading
            granularity: Granularité des prévisions ("hourly", "daily")
            
        Returns:
            List[Dict]: Liste des prévisions
        """
        try:
            headers = get_auth_headers()
            if not headers:
                return []
            
            # Construire l'URL selon la granularité
            endpoint_key = f"forecast_{granularity}"
            if endpoint_key not in self.config.ENDPOINTS_E1:
                print(f"Granularité non supportée: {granularity}")
                return []
            
            url = f"{self.config.ENDPOINTS_E1[endpoint_key]}/{trading_pair_id}"
            
            # Pas de paramètres de date pour récupérer toutes les prévisions
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            else:
                print(f"Erreur lors de la récupération des prévisions: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"Erreur de connexion lors de la récupération des prévisions: {e}")
            return []
    
    def format_chart_data(
        self,
        ohlcv_data: List[Dict[str, Any]],
        forecast_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Formate les données pour l'affichage dans les graphiques.
        
        Args:
            ohlcv_data: Données OHLCV historiques
            forecast_data: Données de prévisions
            
        Returns:
            Dict: Données formatées pour les graphiques
        """
        # Formater les données OHLCV
        ohlcv_formatted = []
        for item in ohlcv_data:
            ohlcv_formatted.append({
                'date': item.get('date'),
                'open': float(item.get('open', 0)),
                'high': float(item.get('high', 0)),
                'low': float(item.get('low', 0)),
                'close': float(item.get('close', 0)),
                'volume': float(item.get('volume_quote', 0))
            })
        
        # Formater les données de prévision
        forecast_formatted = []
        for item in forecast_data:
            forecast_formatted.append({
                'date': item.get('date'),
                'value': float(item.get('value', 0)),
                'model_name': item.get('model_name'),
                'model_version': item.get('model_version')
            })
        
        return {
            'ohlcv': ohlcv_formatted,
            'forecasts': forecast_formatted,
            'last_price': ohlcv_formatted[-1]['close'] if ohlcv_formatted else None,
            'price_change': self._calculate_price_change(ohlcv_formatted),
            'data_count': {
                'historical': len(ohlcv_formatted),
                'forecasts': len(forecast_formatted)
            }
        }
    
    def _calculate_price_change(self, ohlcv_data: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
        """
        Calcule le changement de prix et le pourcentage.
        
        Args:
            ohlcv_data: Données OHLCV formatées
            
        Returns:
            Dict: Changement de prix et pourcentage
        """
        if len(ohlcv_data) < 2:
            return None
        
        current_price = ohlcv_data[-1]['close']
        previous_price = ohlcv_data[-2]['close']
        
        price_change = current_price - previous_price
        price_change_percent = (price_change / previous_price) * 100 if previous_price != 0 else 0
        
        return {
            'absolute': price_change,
            'percent': price_change_percent
        }
