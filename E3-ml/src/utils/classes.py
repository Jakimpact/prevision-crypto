import importlib

import pandas as pd

from src.settings import MLSettings


class TradingPairForecaster:
    def __init__(self, pair_model_info):
        self.trading_pair_id = pair_model_info["id"]
        self.symbol = pair_model_info["symbol"]
        self.base_currency = pair_model_info["base_currency"]
        self.quote_currency = pair_model_info["quote_currency"]
        self.granularity_type = pair_model_info["granularity_type"]
        self.model_name = pair_model_info["model"]
        self.model_params = pair_model_info["params"]
        self.model_instance = self.initialize_model(self.model_name, self.model_params)
        self.historical_forecast = pd.DataFrame(columns=["pred"])
        self.current_forecast = pd.DataFrame(columns=["pred"])

        if self.granularity_type == "daily":
            self.freq = "D"
            self.test_window = 7
            self.test_period_duration = pd.DateOffset(months=6)
            self.test_period_duration_unit = "months"
        elif self.granularity_type == "hourly":
            self.freq = "h"
            self.test_window = 24
            self.test_period_duration = pd.DateOffset(months=1)
            self.test_period_duration_unit = "months"
    
    def initialize_model(self, model_name, params, models_config=MLSettings.models_config):
        """Instancie un modèle (import et création d'objet), à partir des informations du modèles et des paramètres."""

        module = importlib.import_module(models_config[model_name]["darts_module"])
        ModelClass = getattr(module, models_config[model_name]["darts_class"])
        model = ModelClass(**params)
        return model
    
    def add_forecast_to_df(self, forecast, forecast_type):
        """Ajoute une prévision au DataFrame historical_forecast ou current_forecast."""

        forecast_df = forecast.to_dataframe()
        forecast_df = forecast_df.rename(columns={forecast_df.columns[0]: "pred"})

        if forecast_type == "historical_forecast":
            df = pd.concat([self.historical_forecast, forecast_df])
            self.historical_forecast = df
        elif forecast_type == "current_forecast":
            df = pd.concat([self.current_forecast, forecast_df])
            self.current_forecast = df


class TradingPairForecaster_v0:
    def __init__(self, trading_pair_info):
        self.trading_pair_id = trading_pair_info["id"]
        self.symbol = trading_pair_info["symbol"]
        self.base_currency = trading_pair_info["base_currency"]
        self.quote_currency = trading_pair_info["quote_currency"]
        self.granularities = []

    def initialize_granularities(self, trading_pair_info):
        """Initialise les granularités (infos et instance du modèle) pour la paire de trading."""

        for granularity in trading_pair_info["granularities"]:
            if granularity["type"] == "daily":
                freq = "D"
                test_window = 7
            elif granularity["type"] == "hourly":
                freq = "h"
                test_window = 24

            self.granularities.append({
                "type": granularity["type"],
                "freq": freq,
                "test_window": test_window,
                "model_name": granularity["model"],
                "params": granularity["params"],
                "model_instance": self.initialize_model(granularity["model"], granularity["params"]),
                "historical_forecast": pd.DataFrame(columns=["pred"]),
                "current_forecast": pd.DataFrame(columns=["pred"])
            })

    def initialize_model(self, model_name, params, models_config=MLSettings.models_config):
        """Instancie un modèle (import et création d'objet), à partir des informations du modèles et des paramètres."""

        module = importlib.import_module(models_config[model_name]["darts_module"])
        ModelClass = getattr(module, models_config[model_name]["darts_class"])
        model = ModelClass(**params)
        return model
    
    def add_forecast_to_df(self, forecast, granularity, forecast_type):
        """Ajoute une prévision au DataFrame historical_forecast ou current_forecast de la granularité spécifiée."""

        forecast_df = forecast.to_dataframe()
        forecast_df = forecast_df.rename(columns={forecast_df.columns[0]: "pred"})
        granularity[forecast_type] = pd.concat([granularity[forecast_type], forecast_df])