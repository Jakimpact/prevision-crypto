import os

from src.settings import logger, DataSettings


def save_forecasters_models(pair_forecasters, granularity):
    """Enregistre les modèles de prévision pour chaque forecaster."""

    dir_path = DataSettings.models_dir_path + f"/{granularity}_models"
    os.makedirs(dir_path, exist_ok=True)
    
    for forecaster in pair_forecasters:
        filename = os.path.join(dir_path, f"{forecaster.symbol}.pkl")
        forecaster.model_instance.save(filename)
        logger.info(f"Modèle pour {forecaster.symbol} sauvegardé avec succès.")