import json
import os
from pathlib import Path
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from src.settings import ExtractSettings, logger, LogSettings
from src.C2_query.query_currencies import get_currency_by_symbol
from src.C2_query.query_exchanges import get_exchange_by_name
from src.C4_database.models import Currency, Exchange, TradingPair, CryptocurrencyCSV


def process_currency_json(file, session, type):
    """Récupère les données d'un json sur les devises (crypto ou fiat) et les mets en base de données"""
    
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


def process_cd_json(file, session, exchange):
    """Récupère les données du json et mets en base de données les pairs de trading et les infos sur les csv"""

    try:
        with open(file, "r") as f:
            json_data = json.load(f)

        for data in json_data:
            symbol = data["symbol"]
            base = None
            quote = None

            # Gestion spécifique pour Binance
            if exchange.name.lower() == "binance":
                quote_currencies = ["USDT", "BTC", "ETH", "BNB", "USD", "EUR"]
                for quote_curr in quote_currencies:
                    if symbol.endswith(quote_curr):
                        quote = quote_curr
                        base = symbol[:-len(quote_curr)]
                        break
                if not base or not quote:
                    logger.warning(f"Impossible de séparer la paire {symbol} pour Binance")
                    continue
            else:
                try:
                    base, quote = symbol.split('/')
                except ValueError:
                    continue

            base_currency = get_currency_by_symbol(session, base)
            quote_currency = get_currency_by_symbol(session, quote)

            if not base_currency or not quote_currency:
                continue
            
            # Ajout de la pair de trading dans la base de données
            trading_pair = TradingPair(
                base_currency_id=base_currency.id,
                quote_currency_id=quote_currency.id
            )
            session.add(trading_pair)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                # Si la paire existe déjà, on la récupère
                # TODO modif pour faire appel fonction dans dossier query
                trading_pair = session.query(TradingPair).filter_by(
                    base_currency_id=base_currency.id,
                    quote_currency_id=quote_currency.id
                ).first()

            # Création de l'entrée CryptocurrencyCSV
            csv_entry = CryptocurrencyCSV(
                exchange_id=exchange.id,
                trading_pair_id=trading_pair.id,
                timeframe=data["timeframe"],
                start_date=datetime.fromtimestamp(data["start_timestamp"]),
                end_date=datetime.fromtimestamp(data["end_timestamp"]),
                file_url=data["csv_file"]
            )
            session.add(csv_entry)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()

    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")


def process_all_cd_json(session):
    """Récupère les données des json de CryptoDownload et les mets en base de données"""

    files_dir = Path(ExtractSettings.JSON_PATH_CD)
    
    for file in files_dir.iterdir():
        if file.suffix == ".json":
            exchange_name = file.stem.split('_')[0].capitalize()
            
            exchange = get_exchange_by_name(session, exchange_name)
            if not exchange:
                logger.error(f"Exchange {exchange_name} non trouvé dans la base de données")
                continue
            
            logger.info(f"Traitement du fichier {file.name} pour l'exchange {exchange_name}")
            process_cd_json(file, session, exchange)