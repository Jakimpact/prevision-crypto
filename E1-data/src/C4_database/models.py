from sqlalchemy import Column, DateTime, Enum, Integer, Float, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    sign = Column(String, nullable=True)
    type = Column(Enum(enums=["crypto", "fiat"], ordered=False), nullable=False)

    base_pairs = relationship("TradingPair", foreign_keys="TradingPair.base_currency_id", back_populates="base_currency")
    quote_pairs = relationship("TradingPair", foreign_keys="TradingPair.quote_currency_id", back_populates="quote_currency")

    def __repr__(self):
        return f"<Currency(name='{self.name}', symbol='{self.symbol}', type='{self.type}')>"
    

class TradingPair(Base):
    __tablename__ = "trading_pairs"

    id = Column(Integer, primary_key=True)
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    base_currency = relationship("Currency", foreign_keys=[base_currency_id], back_populates="base_pairs")
    quote_currency = relationship("Currency", foreign_keys=[quote_currency_id], back_populates="quote_pairs")
    csv_files = relationship("CryptocurrencyCSV", back_populates="trading_pair")

    def __repr__(self):
        return f"<TradingPair(base='{self.base_currency.symbol}', quote='{self.quote_currency.symbol}')>"


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    csv_files = relationship("CryptocurrencyCSV", back_populates="exchange")

    def __repr__(self):
        return f"<Exchange(name='{self.name}')>"


class CryptocurrencyCSV(Base):
    __tablename__ = "cryptocurrency_CSVs"

    id = Column(Integer, primary_key=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    file_url = Column(String, nullable=False)

    exchange = relationship("Exchange", back_populates="csv_files")
    trading_pair = relationship("TradingPair", back_populates="csv_files")

    def __repr__(self):
        return (f"<CryptocurrencyCSV(exchange='{self.exchange.name}', "
                f"pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"timeframe='{self.timeframe}')>")