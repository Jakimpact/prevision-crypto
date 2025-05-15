import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C1_extraction.extract_coinmarketcap import extract_maps
from src.C1_extraction.extract_cryptodownload import extract_all_json
from src.C1_extraction.extract_csv_data import extract_all_pairs_data
from src.C4_database.feed_db.feed_coinmarketcap import  process_all_cmc_json
from src.C4_database.feed_db.feed_cryptodowload import process_all_cd_json
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande"""

    parser = argparse.ArgumentParser(description="Exécute tous les composants du pipeline E1")
    
    parser.add_argument("--extract", action="store_true", help="Exécute les étapes d'extraction")
    parser.add_argument("--extract_2", action="store_true", help="Exécute le pipeline complet")
    parser.add_argument("--feed_db", action="store_true", help="Exécute les étapes d'alimentation brutes de la base de données")
    parser.add_argument("--aggregate", action="store_true", help="Exécute les étapes d'agrégation")
    parser.add_argument("--clean", action="store_true", help="Exécute les étapes de nettoyage")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")
    
    return parser.parse_args()


def main():
    """Exécute les composants du pipeline E1 en fonction des arguments de la ligne de commande"""

    args = parse_args()
    
    # Si aucun composant n'est spécifié, exécute le pipeline complet
    run_all = args.all or not any([args.extract,
                                   args.extract_2,
                                   args.clean,
                                   args.aggregate
                                ])
    
    # Suivi des variables du pipeline
    logger.info("Exécute les étapes de création / initialisation de la base de données")

    # Extraction des données
    if args.extract or run_all:
        logger.info("Exécute les étapes d'extraction")
        extract_maps()
        extract_all_json()
    
    if args.feed_db or run_all:
        logger.info("Exécute les étapes d'alimentation brutes de la base de données")
        process_all_cmc_json()
        process_all_cd_json()

    # Seconde étape d'extraction
    if args.extract_2 or run_all:
        logger.info("Exécute les étapes d'extraction des données à partir des csv de la bdd")
        extract_all_pairs_data()

    logger.info("Composants du pipeline sélectionnés terminés")

if __name__ == "__main__":
    main()