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
        df = pd.DataFrame({
            "trading_pair_id": trading_pair.id,
            'date': data.date,
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume_quote': data.volume_quote
        } for data in ohlcv_data)

        aggregated_df = df.groupby(["trading_pair_id", "date"], as_index=False).agg({
            "open": lambda x: weighted_average(x, df.loc[x.index, "volume_quote"]),
            "high": "max",
            "low": "min",
            "close": lambda x: weighted_average(x, df.loc[x.index, "volume_quote"]),
            "volume_quote": "sum"
        })

        return aggregated_df
    
    except Exception as e:
        logger.error(f"Erreur lors de l'agrégation des données historique OHLCV pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol}: {e}")
        return None
    

def weighted_average(x, weights):
    """Calcule la moyenne pondérée en gérant le cas où tous les poids sont à 0."""

    if np.sum(weights) == 0:
        return np.mean(x)
    return np.average(x, weights=weights)