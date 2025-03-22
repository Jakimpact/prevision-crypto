import argparse
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C1_extraction.extract_cryptodownload import extract_all_json
from src.C4_database.database import init_db


# Configure la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """Analyse les arguments de la ligne de commande"""

    parser = argparse.ArgumentParser(description="Exécute tous les composants du pipeline E1")
    
    parser.add_argument("--create_db", action="store_true", help="Crée la base de données et le schéma des tables")
    parser.add_argument("--extract", action="store_true", help="Exécute les étapes d'extraction")
    parser.add_argument("--clean", action="store_true", help="Exécute les étapes de nettoyage")
    parser.add_argument("--aggregate", action="store_true", help="Exécute les étapes d'agrégation")
    parser.add_argument("--scrape", action="store_true", help="Exécute les étapes de scraping")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")
    
    return parser.parse_args()


def main():
    """Exécute les composants du pipeline E1 en fonction des arguments de la ligne de commande"""

    args = parse_args()
    
    # Si aucun composant n'est spécifié, exécute le pipeline complet
    run_all = args.all or not any([args.create_db, 
                                   args.extract,
                                   args.clean,
                                   args.aggregate
                                ])
    
    # Suivi des variables du pipeline
    db = None

    # Création / initialisation de la bdd
    if args.create_db or run_all:
        logger.info("Exécute les étapes de création de la base de données")
        engine, Session = init_db()
    
    # Extraction
    if args.extract or run_all:
        logger.info("Exécute les étapes d'extraction")
        # Si la base de données n'existe pas, la crée
        extract_all_json()
    

    logger.info("Composants du pipeline sélectionnés terminés")



if __name__ == "__main__":
    main()