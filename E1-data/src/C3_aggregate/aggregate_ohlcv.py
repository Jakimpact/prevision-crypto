import numpy as np
import pandas as pd

from src.C2_query.query_historical_ohlcv import get_pairs_and_timeframes_from_historical_data, get_historical_ohlcv_by_pair_id_and_timeframe
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
    """Agrège et normalise les enregistrements OHLCV bruts (provenant de CSVHistoricalData) pour une paire & un timeframe.

    Objectif
    --------
    Consolider plusieurs lignes brutes (potentiellement multiples sur une même date pour une paire) en une seule observation
    normalisée par (trading_pair_id, date) prête à être stockée dans la table OHLCV correspondant au timeframe (minute/hour/day).

    Entrées
    -------
    ohlcv_data : Iterable[ORM OHLCV CSVHistoricalData]
        Collection d'objets issus de la couche C2_query (déjà filtrés par paire & timeframe).
    trading_pair : ORM TradingPair
        Objet paire contenant les métadonnées (id, base / quote currencies).
    timeframe : str
        Granularité ciblée (ex: "day", "hour", "2023 minute").

    Sortie
    ------
    pandas.DataFrame
        Colonnes: [trading_pair_id, date, open, close, volume_quote, high, low].
        - open / close : moyennes pondérées par le volume_quote lorsque volume_quote > 0, sinon moyenne simple.
        - volume_quote : somme des volumes agrégés.
        - high / low : extrêmes (max/min) des valeurs intrajournalières / intra-horaires agrégées.
        Retourne None en cas d'erreur et journalise l'exception.
    """

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
            f"Erreur lors de l'agrégation des données OHLCV pour la paire "
            f"{trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}: {e}"
        )
        return None