from sqlalchemy import Column, DateTime, Enum, Integer, Float, ForeignKey, String, UniqueConstraint
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

    __table_args__ = (
        UniqueConstraint("name", "symbol", "type", name="uniq_currency_name_symbol_type")
    )

    def __repr__(self):
        return f"<Currency(name='{self.name}', symbol='{self.symbol}', type='{self.type}')>"
    

class TradingPair(Base):
    __tablename__ = "trading_pairs"

    id = Column(Integer, primary_key=True)
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    quote_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    base_currency = relationship("Currency", foreign_keys=[base_currency_id], back_populates="base_pairs")
    quote_currency = relationship("Currency", foreign_keys=[quote_currency_id], back_populates="quote_pairs")
    csv_files = relationship("CryptocurrencyCSV", foreign_keys="CryptocurrencyCSV.trading_pair_id", back_populates="trading_pair")
    ohlcv_data = relationship("OHLCV", foreign_keys="OHLCV.trading_pair_id", back_populates="trading_pair")

    __table_args__ = (
        UniqueConstraint("base_currency_id", "quote_currency_id", name="uniq_trading_pair")
    )

    def __repr__(self):
        return f"<TradingPair(base='{self.base_currency.symbol}', quote='{self.quote_currency.symbol}')>"


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    csv_files = relationship("CryptocurrencyCSV", foreign_keys="CryptocurrencyCSV.exchange_id", back_populates="exchange")

    def __repr__(self):
        return f"<Exchange(name='{self.name}')>"


class CryptocurrencyCSV(Base):
    __tablename__ = "cryptocurrency_csv"

    id = Column(Integer, primary_key=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    file_url = Column(String, nullable=False)

    exchange = relationship("Exchange", foreign_keys=[exchange_id], back_populates="csv_files")
    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id], back_populates="csv_files")
    historical_data = relationship("CSVHistoricalData", foreign_keys="CSVHistoricalData.csv_file_id", back_populates="csv_file")

    __table_args__ = (
        UniqueConstraint("exchange_id", "trading_pair_id", "timeframe", name="uniq_csv_exchange_trading_pair_timeframe")
    )

    def __repr__(self):
        return (f"<CryptocurrencyCSV(exchange='{self.exchange.name}', "
                f"pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"timeframe='{self.timeframe}')>")
    

class CSVHistoricalData(Base):
    __tablename__ = "csv_historical_data"

    id = Column(Integer, primary_key=True)
    csv_file_id = Column(Integer, ForeignKey("cryptocurrency_csv.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    csv_file = relationship("CryptocurrencyCSV", foreign_keys=[csv_file_id], back_populates="historical_data")

    __table_args__ = (
        UniqueConstraint("csv_file_id", "timestamp", name="uniq_historical_data_csv_file_timestamp")
    )

    def __repr__(self):
        return (f"<CSVHistoricalData(csv_file='{self.csv_file.file_url}', "
                f"timestamp='{self.timestamp}', "
                f"open='{self.open}', high='{self.high}', "
                f"low='{self.low}', close='{self.close}')>")


class OHLCV(Base):
    __tablename__ = "ohlcv"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id], back_populates="ohlcv_data")

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "timestamp", name="uniq_ohlcv_trading_pair_timestamp")
    )

    def __repr__(self):
        return (f"<OHLCV(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"timestamp='{self.timestamp}', open='{self.open}', high='{self.high}',"
                f"low='{self.low}', close='{self.close}', volume='{self.volume})>")