import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C9_data.fetch_data import get_data_for_ml
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande"""

    parser = argparse.ArgumentParser(description="Exécute tous les composants du pipeline E3")
    
    parser.add_argument("--fetch_data", action="store_true", help="Récupère les données depuis l'API E1")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")
    
    return parser.parse_args()


def main():
    """Exécute les composants du pipeline ML en fonction des arguments de la ligne de commande"""

    args = parse_args()
    
    # Si aucun composant n'est spécifié, exécute le pipeline complet
    run_all = args.all or not any([args.fetch_data
                                ])

    logger.info("Démarrage du pipeline ML")

    # Récupération des données
    if args.fetch_data or run_all:
        logger.info("Exécute les étapes de récupération des données")
        get_data_for_ml()
        

    logger.info("Composants du pipeline sélectionnés terminés avec succès")


if __name__ == "__main__":
    main()