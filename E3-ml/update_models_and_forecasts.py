import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C9_data.send_data import save_forecasts_to_db
from src.C9_model.initiate_forecaster import initialize_pair_forecasters_by_granularity
from src.C9_model.predict_model import make_forecasts
from src.C9_model.save_model import save_forecasters_models
from src.C11_monitoring.monitor_training import monitor_trainings
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande."""

    parser = argparse.ArgumentParser(description="Lance l'entraînement des modèles de prévision pour la granularité spécifiée")
    parser.add_argument("--granularity", choices=["hour", "day"], required=True, help="Granularité des modèles (hour ou day)")
    return parser.parse_args()


def main():
    """Exécute l'entraînement des modèles de prévision pour la granularité choisie."""

    args = parse_args()

    logger.info(f"Démarrage du pipeline ML pour la granularity {args.granularity}")

    logger.info("Exécute l'étape d'initialisation des forecasters")
    pair_forecasters = initialize_pair_forecasters_by_granularity(args.granularity)

    logger.info("Exécute l'étape d'évaluation et monitoring des performances à l'entrainement des modèles")
    monitor_trainings(pair_forecasters, args.granularity)

    logger.info("Exécute l'étape d'entrainement et de prévision des modèles")
    make_forecasts(pair_forecasters)

    logger.info("Exécute l'étape de sauvegarde des prévisions")
    save_forecasts_to_db(pair_forecasters)

    logger.info("Exécute l'étape de sauvegarde des modèles")
    save_forecasters_models(pair_forecasters, args.granularity)

    logger.info(f"Pipeline ML terminé pour la granularité {args.granularity}")

if __name__ == "__main__":
    main()