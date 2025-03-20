from sqlalchemy import Column, DateTime, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class CryptocurrencyCSV(Base):
    __tablename__ = "CryptocurrencyCSV"

    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    file_url = Column(String, nullable=False)

    def __repr__(self):
        return f"<CryptoData(symbol='{self.symbol}', timeframe='{self.timeframe}')>"