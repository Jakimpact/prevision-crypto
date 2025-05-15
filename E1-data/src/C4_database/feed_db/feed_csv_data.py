import pandas as pd

from src.C4_database.database import Database
from src.settings import logger, LogSettings


def save_csv_data_to_db(df: pd.DataFrame, db):
    """Ajoute les données d'un dataframe contenant des données OHLCV de fichiers CSV à la base de données."""

    try:
        data_to_insert = df.to_dict(orient="records")
        success_count, failed_entries = db.historical_data.create_many(data_to_insert)
        logger.info(f"Insertion réussie de {success_count} données historiques OHLCV dans la base de données")

        if failed_entries:
            logger.info(f"{len(failed_entries)} lignes non insérées pour les données historiques OHLCV")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données historiques OHLCV issu des CSV dans la base de données : {e}")