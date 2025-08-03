import os
import pickle

from darts.models import XGBModel

from src.settings import DataSettings

def load_model(model_name: str, granularity):
    """Charge un modèle de prévision pour une granularité voulue."""

    model_path = os.path.join(DataSettings.models_dir_path, granularity, f"{model_name}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Le modèle {model_name} n'existe pas.")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model