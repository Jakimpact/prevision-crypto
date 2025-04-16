import json
import os
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from src.settings import ExtractSettings, logger, LogSettings
from src.C4_database.models import Currency, Exchange


def process_currency_json(file, session, type):
    """Récupère les données d'un json sur les monnaies (crypto ou fiat) et les mets en base de données"""
    
    try:
        with open(file, "r") as f:
            json_data = json.load(f)

        success_count = 0
        failed_entries = []

        for data in json_data["data"]:
            currency = Currency(
                name=data["name"],
                symbol=data["symbol"],
                slug=data["slug"] if type == "crypto" else None,
                sign=data["sign"] if type == "fiat" else None,
                rank=data["rank"] if type == "crypto" else None,
                type=type
            )

            session.add(currency)
            try:
                session.commit()
                success_count += 1
            except IntegrityError:
                session.rollback()
                failed_entries.append(currency)

        logger.info(f"Insertion réussie de {success_count} {type} dans la base de données")

        if failed_entries:
            error_file = os.path.join(LogSettings.LOG_PATH, f"failed_{type}_insertion.json")
            with open(error_file, "w") as f:
                json.dump([entry.__dict__ for entry in failed_entries], f, indent=4)
            logger.info(f"{len(failed_entries)} {type} non insérées en raison de doublons ou d'erreurs. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur pendant le traitement des données : {e}")


def process_exchange_json(file, session):
    """Récupère les données du json sur les plateformes d'échanges et les mets en base de données"""

    try:
        with open(file, "r") as f:
            json_data = json.load(f)

        success_count = 0
        failed_entries = []

        for data in json_data["data"]:
            exchange = Exchange(
                name=data["name"],
                slug=data["slug"]
            )

            session.add(exchange)
            try:
                session.commit()
                success_count += 1
            except IntegrityError:
                session.rollback()
                failed_entries.append(exchange)

        logger.info(f"Insertion réussie de {success_count} plateformes d'échanges dans la base de données")

        if failed_entries:
            error_file = os.path.join(LogSettings.LOG_PATH, f"failed_exchange_insertion.json")
            with open(error_file, "w") as f:
                json.dump([entry.__dict__ for entry in failed_entries], f, indent=4)
            logger.info(f"{len(failed_entries)} plateformes d'échanges non insérées en raison de doublons ou d'erreurs. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur pendant le traitement des données : {e}")
    

def process_all_cmc_json(session):
    """Récupère les données des json de CoinMarketCap et les mets en base de données"""

    files_dir = Path(ExtractSettings.JSON_PATH_CMC)

    for file in files_dir.iterdir():
        if file.suffix == ".json":
            if "crypto" in file.stem or "fiat" in file.stem:
                process_currency_json(file, session, type="crypto" if "crypto" in file.stem else "fiat")
            elif "exchange" in file.stem:
                process_exchange_json(file, session)

