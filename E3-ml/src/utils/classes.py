import importlib

import pandas as pd

from src.settings import MLSettings


class TradingPairForecaster:
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
            elif granularity["type"] == "hourly":
                freq = "H"

            self.granularities.append({
                "type": granularity["type"],
                "freq": freq,
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