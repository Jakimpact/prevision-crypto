import requests

import pandas as pd

from src.C2_query.query_currencies import get_currency_by_name
from src.C2_query.query_ohlcv_daily import get_last_ohlcv_daily_by_pair_id
from src.C2_query.query_ohlcv_hourly import get_last_ohlcv_hourly_by_pair_id
from src.C2_query.query_trading_pairs import get_trading_pair_by_currencies
from src.C4_database.database import Database
from src.C4_database.feed_db.feed_ohlcv_data import save_ohlcv_data_to_db
from src.settings import logger, UpdateSettings
from src.utils.functions import datetime_to_milliseconds


def update_all_ohlcv_pairs(frequency):
    """
    Met à jour les données OHLCV à partir Binance,
    pour les paires de tradings sélectionnées ayant la granularité spécifiée.
    """

    for pair in UpdateSettings.TRADING_PAIRS:
        if frequency in pair["timeframes"]:
            with Database() as db:

                base_currency = get_currency_by_name(pair["base_name"], session=db.session)
                quote_currency = get_currency_by_name(pair["quote_name"], session=db.session)
                trading_pair = get_trading_pair_by_currencies(base_currency.id, quote_currency.id, session=db.session)
                if not all([base_currency, quote_currency, trading_pair]):
                    logger.warning(f"Pair de trading {pair['base_name']}/{pair['quote_name']} non trouvé dans la base de données")
                    continue
                
                if frequency == "hour":
                    db_model = db.ohlcv_hourly
                    last_entry = get_last_ohlcv_hourly_by_pair_id(trading_pair.id, session=db.session)
                elif frequency == "day":
                    db_model = db.ohlcv_daily
                    last_entry = get_last_ohlcv_daily_by_pair_id(trading_pair.id, session=db.session)
                if last_entry is None:
                    logger.warning(f"Aucune donnée OHLCV trouvée pour la paire {pair['base_name']}/{pair['quote_name']} en {frequency}")
                    continue

                df = fetch_binance_data(trading_pair, frequency, last_entry)
                save_ohlcv_data_to_db(df, trading_pair, frequency, db_model)


def fetch_binance_data(trading_pair, frequency, last_entry):
    """
    Récupère les données OHLCV depuis Binance pour une paire de trading spécifique
    et une fréquence donnée, en commençant à partir de la dernière entrée connue.
    """

    url = UpdateSettings.BINANCE_OHLCV_URL
    symbol = f"{trading_pair.base_currency.symbol}{trading_pair.quote_currency.symbol}"
    start_timestamp = datetime_to_milliseconds(last_entry.date)
    if frequency == "hour":
        # Ajoute 1 heure (3600000 ms)
        start_timestamp += 3600000
        interval = "1h"
    elif frequency == "day":
        # Ajoute 1 jour (86400000 ms)
        start_timestamp += 86400000
        interval = "1d"

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_timestamp
    }

    data_fetched = []
    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
        ])
        df = df[["open_time", "open", "high", "low", "close", "quote_asset_volume"]]
        df = df.rename(columns={"open_time": "date", "quote_asset_volume": "volume_quote"})

        df["date"] = pd.to_datetime(df["date"], unit="ms")
        # on garder uniquement les lignes dont date < now (on ne veut pas de données pas encore clôturées)
        if frequency == "hour":
            now = pd.Timestamp.utcnow().replace(minute=0, second=0, microsecond=0).tz_localize(None)
        elif frequency == "day":
            now = pd.Timestamp.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).tz_localize(None)
        df = df[df["date"] < now]

        df["trading_pair_id"] = trading_pair.id
        data_fetched.append(df)

        # On arrête la boucle si on a moins de 500 résultats (limite de base de l'API Binance)
        if len(data) < 500:
            break
        # Sinon, on prépare la prochaine requête à partir du prochain open_time (heure ou jour suivant)
        if frequency == "hour":
            next_time = df["date"].max() + pd.Timedelta(hours=1)
        elif frequency == "day":
            next_time = df["date"].max() + pd.Timedelta(days=1)
        params["startTime"] = int(next_time.timestamp() * 1000)

    if len(data_fetched) > 1:
        df = pd.concat(data_fetched, ignore_index=True)
    else:
        df = data_fetched[0]
        
    return df
