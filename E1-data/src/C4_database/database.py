import os
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.C4_database.crud import (
    CurrencyCRUD, 
    TradingPairCRUD, 
    ExchangeCRUD, 
    CryptocurrencyCSVCRUD, 
    CSVHistoricalDataCRUD, 
    OHLCVCRUD,
    UserCRUD
)
from src.C4_database.models import Base
from src.settings import DatabaseSettings


db_path = DatabaseSettings.DB_PATH
db_filename = DatabaseSettings.DB_FILENAME


os.makedirs(db_path, exist_ok=True)
engine = create_engine(f'sqlite:///{db_path}/{db_filename}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def with_session(func):
    @wraps(func)
    def wrapper(*args, session=None, **kwargs):
        if session is not None:
            return func(*args, session=session, **kwargs)
        else:
            with Database() as db:
                return func(*args, session=db.session, **kwargs)
    return wrapper


class Database:
    def __init__(self):
        self.session = Session()

        # Initialisation des objets CRUD
        self.currencies = CurrencyCRUD(self.session)
        self.trading_pairs = TradingPairCRUD(self.session)
        self.exchanges = ExchangeCRUD(self.session)
        self.crypto_csvs = CryptocurrencyCSVCRUD(self.session)
        self.historical_data = CSVHistoricalDataCRUD(self.session)
        self.ohlcv = OHLCVCRUD(self.session)
        self.users = UserCRUD(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()