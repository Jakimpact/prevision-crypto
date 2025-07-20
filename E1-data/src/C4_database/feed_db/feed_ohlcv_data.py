import pandas as pd

from src.settings import logger


def save_ohlcv_data_to_db(aggregated_df: pd.DataFrame, trading_pair, timeframe, db_model):
    """Enregistre les données OHLCV pour un modèle défini (minute, hourly, daily) dans la base de données."""

    try:
        data_to_insert = aggregated_df.to_dict(orient="records")
        success_count, failed_entries = db_model.create_many(data_to_insert)
        logger.info(f"Insertion réussie de {success_count} données OHLCV dans la base de données pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}")

        if failed_entries:
            logger.info(f"{len(failed_entries)} lignes non insérées pour les données OHLCV de la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données OHLCV dans la base de données pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe} : {e}")