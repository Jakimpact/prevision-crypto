from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session

from src.C4_database.models import (
    Base, 
    Currency, 
    TradingPair, 
    Exchange, 
    CryptocurrencyCSV, 
    CSVHistoricalData, 
    OHLCV,
    User
)
from src.utils.functions import validate_date


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
        
    def get_pairs_by_base_currency_symbol(self, symbol: str):
        """Récupère toutes les paires pour lesquelles le symbol donné apparaît comme base currency."""
        pairs = (self.db.query(self.model)
                .options(joinedload(self.model.base_currency),
                        joinedload(self.model.quote_currency))
                .filter(self.model.base_currency.has(Currency.symbol == symbol))
                .all())
        return pairs

    def get_pair_by_currency_symbols(self, base_symbol: str, quote_symbol: str):
        """Récupère une paire de trading spécifique à partir des symbols des currency base et quote."""
        pair = (self.db.query(self.model)
                .options(joinedload(self.model.base_currency),
                        joinedload(self.model.quote_currency))
                .filter(self.model.base_currency.has(Currency.symbol == base_symbol))
                .filter(self.model.quote_currency.has(Currency.symbol == quote_symbol))
                .first())
        return pair


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
    
    def get_ohlcv_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        """
        Récupère les données OHLCV pour une paire de trading.
        Si start_date est fourni, ne retourne que les données à partir de cette date.
        Args:
            trading_pair_id: ID de la paire de trading
            start_date: Date de début au format 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
        """
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
                
        return query.order_by(self.model.date.asc()).all()


class UserCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str):
        """Récupère un utilisateur par son nom d'utilisateur."""
        return self.db.query(self.model).filter(self.model.username == username).first()