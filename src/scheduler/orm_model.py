from datetime import datetime
from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import (
    Integer, String, DateTime, Numeric, BigInteger,
    ForeignKey, UniqueConstraint, Index, Boolean
)

Base = declarative_base()


class InstrumentQuote(Base):
    __tablename__ = "trading_instrumentquote"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    instrument_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    bid_price: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    bid_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    ask_price: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    ask_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_price: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    exchange: Mapped[str] = mapped_column(String(20), nullable=False)
    market_state: Mapped[str] = mapped_column(String(20), nullable=False)

    daily_change: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    daily_change_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False, default=0)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class InstrumentIntervalData(Base):
    __tablename__ = "trading_instrumentintervaldata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    high_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    low_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    close_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)

    volume: Mapped[int] = mapped_column(BigInteger, nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("instrument_id", "start_time", name="interval_unique_idx"),
        Index("instrument_start_idx", "instrument_id", "start_time"),
    )

class Instrument(Base):
    __tablename__ = "trading_instrument"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    symbol: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    exchange: Mapped[str] = mapped_column(String(32), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
