import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C1_extraction.extract_binance_data import update_all_ohlcv_pairs
from src.settings import logger


def parse_args():
    """Analyse les arguments de la ligne de commande."""

    parser = argparse.ArgumentParser(description="Met à jour les données OHLCV dans la base de données")
    parser.add_argument("--frequency", choices=["hour", "day"], required=True, help="Fréquence de mise à jour (hour ou day)")
    return parser.parse_args()


def main():
    """Exécute la mise à jour OHLCV selon la fréquence choisie."""

    args = parse_args()

    logger.info(f"Démarrage de la mise à jour OHLCV ({args.frequency})")

    # Récupération des données pour les paires de trading à mettre à jour et mise en base de données
    update_all_ohlcv_pairs(args.frequency)

    logger.info("Mise à jour OHLCV terminée")


if __name__ == "__main__":
    main()