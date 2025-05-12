from typing import List, Dict

from sqlalchemy.exc import IntegrityError
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
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError:
            self.db.rollback()
            raise

    def create_many(self, items: List[Dict], bulk: bool=True):
        """
        Méthode pour insérer plusieurs objets dans la base de données.
        Retourne le nombre d'objets insérés avec succès et une liste des objets qui n'ont pas pu être insérés
        """
        success = []
        failed = []

        # Essai de créer les objets avec un bulk 
        if bulk:
            try:
                self.db.bulk_insert_mappings(self.model, items)
                self.db.commit()
                return len(items), []
            except IntegrityError:
                self.db.rollback()

        # Si le bulk échoue, on les insère un par un
        for data in items:
            try:
                self.create(**data)
                success.append(data)
            except IntegrityError:
                failed.append(data)
        
        return len(success), failed

    def get(self, id: int):
        return self.db.query(self.model).get(id)

    def list_all(self):
        return self.db.query(self.model).all()

    def update(self, id: int, **kwargs):
        obj = self.get(id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError:
            self.db.rollback()
            raise

    def delete(self, id: int):
        obj = self.get(id)
        try:    
            self.db.delete(obj)
            self.db.commit()
            return obj
        except IntegrityError:
            self.db.rollback()
            raise
    

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