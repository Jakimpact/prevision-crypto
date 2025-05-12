from sqlalchemy.orm import Session

from src.C4_database.models import (
    Base, 
    Currency, 
    TradingPair, 
    Exchange, 
    CryptocurrencyCSV, 
    CSVHistoricalData, 
    OHLCV
)


class BaseCRUD:
    def __init__(self, model, db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, id: int):
        return self.db.query(self.model).get(id)

    def list_all(self):
        return self.db.query(self.model).all()

    def update(self, id: int, **kwargs):
        obj = self.get(id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int):
        obj = self.get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj
    

class CurrencyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(Currency, db)


class TradingPairCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(TradingPair, db)


class ExchangeCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(Exchange, db)


class CryptocurrencyCSVCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(CryptocurrencyCSV, db)


class CSVHistoricalDataCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(CSVHistoricalData, db)


class OHLCVCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(OHLCV, db)