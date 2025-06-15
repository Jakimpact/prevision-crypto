import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C1_extraction.extract_coinmarketcap import extract_maps
from src.C1_extraction.extract_cryptodownload import extract_all_json
from src.C1_extraction.extract_csv_data import extract_all_pairs_data
from src.C3_aggregate.aggregate_ohlcv import aggregate_all_ohlcv_by_minute, aggregate_all_ohlcv_by_hour_and_day
from src.C4_database.feed_db.feed_coinmarketcap import  process_all_cmc_json
from src.C4_database.feed_db.feed_cryptodowload import process_all_cd_json
from src.C4_database.feed_db.feed_user import create_initial_api_user
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande"""

    parser = argparse.ArgumentParser(description="Exécute tous les composants du pipeline E1")
    
    parser.add_argument("--extract_files", action="store_true", help="Exécute les étapes d'extraction des fichiers")
    parser.add_argument("--feed_raw_db", action="store_true", help="Exécute les étapes d'alimentation brutes de la base de données")
    parser.add_argument("--extract_data", action="store_true", help="Exécute les étapes d'extraction des données")
    parser.add_argument("--aggregate", action="store_true", help="Exécute les étapes d'agrégation")
    parser.add_argument("--initiate_api_user", action="store_true", help="Exécute les étapes d'initialisation de l'utilisateur API")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")
    parser.add_argument("--tmp", action="store_true", help="Exécute les étapes temporaires (non implémentées)")
    
    return parser.parse_args()


def main():
    """Exécute les composants du pipeline ETL en fonction des arguments de la ligne de commande"""

    args = parse_args()
    
    # Si aucun composant n'est spécifié, exécute le pipeline complet
    run_all = args.all or not any([args.extract_files,
                                   args.feed_raw_db,
                                   args.extract_data,
                                   args.aggregate,
                                   args.initiate_api_user,
                                   args.tmp
                                ])

    logger.info("Démarrage du pipeline ETL")

    # Extraction de fichiers JSON et CSV
    if args.extract_files or run_all:
        logger.info("Exécute les étapes d'extraction des fichiers")
        extract_maps()
        extract_all_json()
    
    if args.feed_raw_db or run_all:
        logger.info("Exécute les étapes d'alimentation brutes de la base de données")
        process_all_cmc_json()
        process_all_cd_json()

    # Extraction des données à partir des fichiers CSV
    if args.extract_data or run_all:
        logger.info("Exécute les étapes d'extraction des données à partir des csv de la bdd")
        extract_all_pairs_data()

    # Agrégation des données
    if args.aggregate or run_all:
        logger.info("Exécute les étapes d'agrégation")
        aggregate_all_ohlcv_by_minute()

    if args.tmp:
        aggregate_all_ohlcv_by_hour_and_day()

    # Initialisation de l'utilisateur API
    if args.initiate_api_user or run_all:
        logger.info("Exécute les étapes d'initialisation de l'utilisateur API")
        create_initial_api_user()
        
    logger.info("Composants du pipeline ETL sélectionnés terminés avec succès")


if __name__ == "__main__":
    main()