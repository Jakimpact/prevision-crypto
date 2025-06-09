import numpy as np
import pandas as pd

from src.C2_query.query_historical_ohlcv import get_all_pairs_from_historical_data, get_historical_ohlcv_by_pair_id
from src.C4_database.database import Database
from src.C4_database.feed_db.feed_ohlcv_data import save_ohlcv_data_to_db
from src.settings import logger



def aggregate_all_ohlcv():
    """Agrège les données OHLCV de toutes les paires de trading et les enregistre dans la base de données."""

    with Database() as db:

        trading_pairs = get_all_pairs_from_historical_data(session=db.session)
        if not trading_pairs:
            logger.warning("Aucune paire de trading trouvée dans les données historiques OHLCV")
            return

        for trading_pair in trading_pairs:
            ohlcv_data = get_historical_ohlcv_by_pair_id(trading_pair.id, session=db.session)
            aggregated_df = aggregate_ohlcv_data(ohlcv_data, trading_pair)
            save_ohlcv_data_to_db(aggregated_df, trading_pair, db)


def aggregate_ohlcv_data(ohlcv_data, trading_pair):
    """Agrège les données OHLCV de la table CSVHistoricalData d'une paire de trading spécifique."""

    try:
        records = [(data.date, data.open, data.high, data.low, data.close, data.volume_quote)
                   for data in ohlcv_data]

        df = pd.DataFrame.from_records(records, columns=["date", "open", "high", "low", "close", "volume_quote"])
        df["trading_pair_id"] = trading_pair.id

        df["weighted_open"] = df["open"] * df["volume_quote"]
        df["weighted_close"] = df["close"] * df["volume_quote"]

        aggregated_df = df.groupby(["trading_pair_id", "date"], as_index=False).agg({
            "weighted_open": "sum",
            "weighted_close": "sum",
            "open": "mean", # dans le cas où volume_quote == 0
            "close": "mean", # dans le cas où volume_quote == 0
            "volume_quote": "sum",
            "high": "max",
            "low": "min"
        })

        # Moyenne pondérée ou moyenne simple selon si le volume_quote est égale à 0
        aggregated_df["open"] = np.where(
            aggregated_df["volume_quote"] == 0,
            aggregated_df["open"],
            aggregated_df["weighted_open"] / aggregated_df["volume_quote"]
        )
        aggregated_df["close"] = np.where(
            aggregated_df["volume_quote"] == 0,
            aggregated_df["close"],
            aggregated_df["weighted_close"] / aggregated_df["volume_quote"]
        )

        aggregated_df = aggregated_df.drop(columns=["weighted_open", "weighted_close"])

        return aggregated_df

    except Exception as e:
        logger.error(
            f"Erreur lors de l'agrégation des données OHLCV pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol}: {e}"
        )
        return None