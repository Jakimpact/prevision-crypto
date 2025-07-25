from sqlalchemy import Column, DateTime, Integer, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


Base = declarative_base()


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    sign = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)
    rank_date = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    type = Column(String, nullable=False)

    base_pairs = relationship("TradingPair", foreign_keys="TradingPair.base_currency_id", back_populates="base_currency")
    quote_pairs = relationship("TradingPair", foreign_keys="TradingPair.quote_currency_id", back_populates="quote_currency")

    __table_args__ = (
        UniqueConstraint("name", "symbol", "rank", "type", name="uniq_currency_name_symbol_rank_type"),
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
    ohlcv_minute_data = relationship("OHLCVMinute", foreign_keys="OHLCVMinute.trading_pair_id", back_populates="trading_pair")
    ohlcv_hourly_data = relationship("OHLCVHourly", foreign_keys="OHLCVHourly.trading_pair_id", back_populates="trading_pair")
    ohlcv_daily_data = relationship("OHLCVDaily", foreign_keys="OHLCVDaily.trading_pair_id", back_populates="trading_pair")

    __table_args__ = (
        UniqueConstraint("base_currency_id", "quote_currency_id", name="uniq_trading_pair"),
    )

    def __repr__(self):
        return f"<TradingPair(base='{self.base_currency.symbol}', quote='{self.quote_currency.symbol}')>"


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)

    csv_files = relationship("CryptocurrencyCSV", foreign_keys="CryptocurrencyCSV.exchange_id", back_populates="exchange")

    __table_args__ = (
        UniqueConstraint("name", "slug", name="uniq_exchange_name_slug"),
    )

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
        UniqueConstraint("exchange_id", "trading_pair_id", "timeframe", name="uniq_csv_exchange_trading_pair_timeframe"),
    )

    def __repr__(self):
        return (f"<CryptocurrencyCSV(exchange='{self.exchange.name}', "
                f"pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"timeframe='{self.timeframe}')>")
    

class CSVHistoricalData(Base):
    __tablename__ = "csv_historical_data"

    id = Column(Integer, primary_key=True)
    csv_file_id = Column(Integer, ForeignKey("cryptocurrency_csv.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume_quote = Column(Float, nullable=False)

    csv_file = relationship("CryptocurrencyCSV", foreign_keys=[csv_file_id], back_populates="historical_data")

    __table_args__ = (
        UniqueConstraint("csv_file_id", "date", name="uniq_historical_data_csv_file_date"),
    )

    def __repr__(self):
        return (f"<CSVHistoricalData(csv_file='{self.csv_file.file_url}', "
                f"date='{self.date}', "
                f"open='{self.open}', high='{self.high}', "
                f"low='{self.low}', close='{self.close}')>")


class OHLCVMinute(Base):
    __tablename__ = "ohlcv_minute"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume_quote = Column(Float, nullable=False)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id], back_populates="ohlcv_minute_data")

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_ohlcv_minute_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<OHLCVMinute(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', open='{self.open}', high='{self.high}',"
                f"low='{self.low}', close='{self.close}', volume='{self.volume})>")


class OHLCVHourly(Base):
    __tablename__ = "ohlcv_hourly"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume_quote = Column(Float, nullable=False)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id], back_populates="ohlcv_hourly_data")

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_ohlcv_hourly_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<OHLCVHourly(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', open='{self.open}', high='{self.high}',"
                f"low='{self.low}', close='{self.close}', volume='{self.volume})>")


class OHLCVDaily(Base):
    __tablename__ = "ohlcv_daily"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume_quote = Column(Float, nullable=False)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id], back_populates="ohlcv_daily_data")

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_ohlcv_daily_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<OHLCVDaily(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', open='{self.open}', high='{self.high}',"
                f"low='{self.low}', close='{self.close}', volume='{self.volume})>")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hashed = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    role = Column(String, nullable=False, default="user")

    def __repr__(self):
        return f"<User(username='{self.username}', status='{self.status}', role='{self.role}')>"
    

class ForecastMinute(Base):
    __tablename__ = "forecast_minute"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id])

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_forecast_minute_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<ForecastMinute(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', value='{self.value}'>")
    

class ForecastHourly(Base):
    __tablename__ = "forecast_hourly"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id])

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_forecast_hourly_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<ForecastHourly(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', value='{self.value}'>")
    

class ForecastDaily(Base):
    __tablename__ = "forecast_daily"

    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)

    trading_pair = relationship("TradingPair", foreign_keys=[trading_pair_id])

    __table_args__ = (
        UniqueConstraint("trading_pair_id", "date", name="uniq_forecast_daily_trading_pair_date"),
    )

    def __repr__(self):
        return (f"<ForecastDaily(pair='{self.trading_pair.base_currency.symbol}/{self.trading_pair.quote_currency.symbol}', "
                f"date='{self.date}', value='{self.value}'>")