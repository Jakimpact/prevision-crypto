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

    def create_many(self, items: List[Dict], batch_size: int=10000):
        """
        Méthode pour insérer plusieurs objets dans la base de données.
        Retourne le nombre d'objets insérés avec succès et une liste des objets qui n'ont pas pu être insérés
        """
        sucess_count = 0
        failed = []
        
        # On essaie d'insérer les objets en batch
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]

            try:
                self.db.bulk_insert_mappings(self.model, batch)
                self.db.commit()
                sucess_count += len(batch)

            # Si le bulk échoue, on rollback et on essaie d'ajouter les objets un par un
            except IntegrityError:
                self.db.rollback()
                for item in batch:
                    try:
                        self.create(**item)
                        sucess_count += 1
                    # Si l'insertion échoue, on ajoute l'objet à la liste des échecs
                    except IntegrityError:
                        failed.append(item)

        return sucess_count, failed


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