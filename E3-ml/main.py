import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C9_data.fetch_data import get_data_for_ml
from src.C9_model.evaluate_model import test_past_performances
from src.C9_model.initiate_forecaster import initialize_trading_pairs_forecasters
from src.C9_model.predict_model import make_forecasts
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande"""

    parser = argparse.ArgumentParser(description="Exécute tous les composants du pipeline E3")
    
    parser.add_argument("--fetch_data", action="store_true", help="Récupère les données depuis l'API E1")
    parser.add_argument("--evaluate", action="store_true", help="Lance l'étape d'évaluation des modèles")
    parser.add_argument("--predict", action="store_true", help="Lance l'étape de prévision des modèles")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")
    
    return parser.parse_args()


def main():
    """Exécute les composants du pipeline ML en fonction des arguments de la ligne de commande"""

    args = parse_args()
    
    # Si aucun composant n'est spécifié, exécute le pipeline complet
    run_all = args.all or not any([args.fetch_data,
                                   args.evaluate,
                                    args.predict
                                ])

    logger.info("Démarrage du pipeline ML")

    # Récupération des données
    if args.fetch_data or run_all:
        logger.info("Exécute les étapes de récupération des données")
        get_data_for_ml()

    # Initialisation des pairs de trading à forecaster
    if any([args.evaluate, args.predict]) or run_all:
        logger.info("Exécute les étapes d'initialisation des pairs de trading à forecaster")
        trading_pair_forecasters = initialize_trading_pairs_forecasters()

    # Évaluation des modèles
    if any([args.evaluate, args.predict]) or run_all:
        logger.info("Exécute les étapes d'évaluation des modèles")
        test_past_performances(trading_pair_forecasters)
    
    # Prévisions des modèles
    if args.predict or run_all:
        logger.info("Exécute les étapes de prévision des modèles")
        make_forecasts(trading_pair_forecasters)

    logger.info("Composants du pipeline sélectionnés terminés avec succès")


if __name__ == "__main__":
    main()