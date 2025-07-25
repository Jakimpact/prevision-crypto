import numpy as np
import pandas as pd

from src.C2_query.query_historical_ohlcv import get_all_pairs_from_historical_data, get_historical_ohlcv_by_pair_id, get_pairs_and_timeframes_from_historical_data, get_historical_ohlcv_by_pair_id_and_timeframe
from src.C2_query.query_ohlcv_minute import get_all_pairs_from_ohlcv_minute, get_ohlcv_minute_by_pair_id
from src.C4_database.database import Database
from src.C4_database.feed_db.feed_ohlcv_data import save_ohlcv_data_to_db
from src.settings import logger


def aggregate_all_ohlcv():
    """
    Agrège les données OHLCV par date de toutes les paires de trading pour chaque timeframe différent, à partir de la table CSVHistoricalData.
    Enregistre les données agrégés dans la table ohlcv du timeframe correspondant.
    """
    
    with Database() as db:

        pairs_and_timeframes = get_pairs_and_timeframes_from_historical_data(session=db.session)
        if not pairs_and_timeframes:
            logger.warning("Aucune paire de trading trouvée dans les données historiques OHLCV")
            return
        
        for pair_and_timeframe in pairs_and_timeframes:
            ohlcv_data = get_historical_ohlcv_by_pair_id_and_timeframe(pair_and_timeframe[0].id, pair_and_timeframe[1], session=db.session)
            aggregated_df = aggregate_ohlcv_data(ohlcv_data, pair_and_timeframe[0], pair_and_timeframe[1])

            if pair_and_timeframe[1] == "day":
                db_model = db.ohlcv_daily
            elif pair_and_timeframe[1] == "hour":
                db_model = db.ohlcv_hourly
            elif pair_and_timeframe[1].endswith("minute"):
                db_model = db.ohlcv_minute

            save_ohlcv_data_to_db(aggregated_df, pair_and_timeframe[0], pair_and_timeframe[1], db_model)


def aggregate_ohlcv_data(ohlcv_data, trading_pair, timeframe):
    "Agrège les données OHLCV de la table CSVHistoricalData d'une paire de trading spécifique."

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
            f"Erreur lors de l'agrégation des données OHLCV pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}: {e}"
        )
        return None


# Anciennes fonctions d'agrégation, à conserver pour référence

def aggregate_all_ohlcv_by_minute():
    """Agrège les données OHLCV de toutes les paires de trading à la minute à partir de la table CSVHistoricalData et les enregistre dans la base de données."""

    with Database() as db:

        trading_pairs = get_all_pairs_from_historical_data(session=db.session)
        if not trading_pairs:
            logger.warning("Aucune paire de trading trouvée dans les données historiques OHLCV")
            return

        for trading_pair in trading_pairs:
            ohlcv_data = get_historical_ohlcv_by_pair_id(trading_pair.id, session=db.session)
            aggregated_df = aggregate_ohlcv_data_by_minute(ohlcv_data, trading_pair)
            save_ohlcv_data_to_db(aggregated_df, trading_pair, db.ohlcv_minute)


def aggregate_all_ohlcv_by_hour_and_day():
    """Agrège les données OHLCV de toutes les paires de trading par heure et par jour à partir de la table OHLCVMinute et les enregistre dans la base de données."""

    with Database() as db:

        trading_pairs = get_all_pairs_from_ohlcv_minute(session=db.session)
        if not trading_pairs:
            logger.warning("Aucune paire de trading trouvée dans les données OHLCV minute")
            return
        
        for trading_pair in trading_pairs:
            ohlcv_minute_data = get_ohlcv_minute_by_pair_id(trading_pair.id, session=db.session)
            aggregated_hourly_df = aggregate_ohlcv_data_by_freq(ohlcv_minute_data, "h", trading_pair)
            save_ohlcv_data_to_db(aggregated_hourly_df, trading_pair, db.ohlcv_hourly)
            aggregated_daily_df = aggregate_ohlcv_data_by_freq(ohlcv_minute_data, "D", trading_pair)
            save_ohlcv_data_to_db(aggregated_daily_df, trading_pair, db.ohlcv_daily)


def aggregate_ohlcv_data_by_minute(ohlcv_data, trading_pair):
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
    

def aggregate_ohlcv_data_by_freq(ohlcv_minute_data, freq, trading_pair):
    """
    Aggrège les données OHLCV de la table OHLCVMinute d'une paire de trading spécifique
    à la fréquence souahitée ("h" pour heure et "D" pour jour).
    """

    try:
        records = [(data.date, data.open, data.high, data.low, data.close, data.volume_quote)
                   for data in ohlcv_minute_data]
        df = pd.DataFrame.from_records(records, columns=["date", "open", "high", "low", "close", "volume_quote"])
        df = df.sort_values("date")

        # Groupe par la fréquence souhaitée
        grouped_df = df.groupby(pd.Grouper(key='date', freq=freq))
        aggregated_df = grouped_df.agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume_quote": "sum"
        }).reset_index()

        # On supprime les lignes où open, high, low, close sont NaN (données manquantes créé par le pd.Grouper)
        aggregated_df = aggregated_df.dropna(subset=["open", "high", "low", "close"])
        aggregated_df["trading_pair_id"] = trading_pair.id

        return aggregated_df

    except Exception as e:
        logger.error(
            f"Erreur lors de l'agrégation des données OHLCV à la fréquence {freq} pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol}: {e}"
        )
        return None