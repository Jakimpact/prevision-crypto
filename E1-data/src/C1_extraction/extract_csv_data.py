import io
import requests
from datetime import datetime

import pandas as pd

from src.C2_query.query_currencies import get_currency_by_name
from src.C2_query.query_trading_pairs import get_trading_pair_by_currencies
from src.C2_query.query_crypto_csv import search_crypto_csvs_by_trading_pair_and_timeframe
from src.C4_database.database import Database
from src.C4_database.feed_db.feed_csv_data import save_csv_data_to_db
from src.settings import ExtractSettings, logger
from src.utils.functions import parse_date


def extract_all_pairs_data(trading_pairs_to_extract=ExtractSettings.TRADING_PAIRS):
    """Lance l'extraction des données à partir des csv de la bdd pour toutes les pairs de trading renseignées."""

    for pair_to_extract in trading_pairs_to_extract:
        with Database() as db:

            base_currency = get_currency_by_name(pair_to_extract["base_name"], session=db.session)
            quote_currency = get_currency_by_name(pair_to_extract["quote_name"], session=db.session)
            trading_pair = get_trading_pair_by_currencies(base_currency.id, quote_currency.id, session=db.session)
            if not all([base_currency, quote_currency, trading_pair]):
                logger.warning(f"Pair de trading {pair_to_extract['base_name']}/{pair_to_extract['quote_name']} non trouvé dans la base de données")
                continue
            
            # Modifier pour intégrer les différents timeframes dans les csv to extract
            csvs_to_extract = []
            for timeframe in pair_to_extract["timeframes"]:
                csvs = search_crypto_csvs_by_trading_pair_and_timeframe(trading_pair.id, timeframe, session=db.session)
                if csvs:
                    csvs_to_extract.extend(csvs)

            if not csvs_to_extract:
                logger.warning(f"Pas de fichier csv dans la base de données pour la pair de trading {pair_to_extract['base_name']}/{pair_to_extract['quote_name']} et le timeframe {timeframe}")
                continue
            
            for crypto_csv in csvs_to_extract:
                csv_year = extract_year_from_timeframe(crypto_csv.timeframe)
                if csv_year:
                    if (csv_year < pair_to_extract["from_year"]):
                        continue

                df = read_csv_data(crypto_csv, pair_to_extract["from_year"], csv_year)
                if df is not None:
                    save_csv_data_to_db(df, db, crypto_csv)
                else:
                    logger.warning(f"Aucune donnée valide trouvée dans le csv {crypto_csv.file_url} pour la pair de trading {pair_to_extract['base_name']}/{pair_to_extract['quote_name']} et le timeframe {crypto_csv.timeframe}")


def extract_year_from_timeframe(timeframe):
    """Extrait l'année du timeframe si elle est présente en début de chaine."""
    
    parts = timeframe.strip().split()
    if len(parts) > 1:
        first_part = parts[0]
        if first_part.isdigit() and len(first_part) == 4:
            return int(first_part)
    return None


def read_csv_data(crypto_csv, start_year, csv_year):
    """Lit et formate les données d'un fichier CSV récupéré depuis une URL pour les retourner sous forme de DataFrame."""

    try:
        response = requests.get(crypto_csv.file_url)
        response.raise_for_status()
        csv_io = io.StringIO(response.text)

        quote_symbol = crypto_csv.trading_pair.quote_currency.symbol.lower()

        df = pd.read_csv(csv_io, sep=",", header=1)
        df.columns = df.columns.str.lower()

        # Sélectionne la bonne colonne de volume selon le nommage fait dans les fichiers CSV
        volumes_col_names = [f"volume {quote_symbol}", "volume_from"]
        volume_col_name = next((col for col in volumes_col_names if col in df.columns), None)

        df = df[["date", "open", "high", "low", "close", volume_col_name]]
        df = df.rename(columns={volume_col_name: "volume_quote"})

        # Gestion des dates
        if crypto_csv.timeframe == "day":
            df["date"] = df["date"].apply(parse_date)
            df["date"] = df["date"].dt.normalize()
        else:
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        df = df.dropna(subset=["date"])

        # Filtrage des données pour garder uniquement celles à partir de start_year
        df = df[df["date"].dt.year >= start_year]
        # Filtrage des données pour garder uniquement celles de l'année du csv si spécifiée dans le csv
        if csv_year:
            df = df[df["date"].dt.year == csv_year]

        # Ajout des colonnes manquantes
        df["csv_file_id"] = crypto_csv.id

        return df

    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier CSV {crypto_csv.file_url}: {e}")
        return None