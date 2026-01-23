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

    instrument: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

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

class Fund(Base):
    __tablename__ = "funds_fund"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creator_portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("users_userportfolio.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_units: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    nav_per_unit: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False, default=1)


class FundHolding(Base):
    __tablename__ = "funds_fundholding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds_fund.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    weight_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)


class FundNAVHistory(Base):
    __tablename__ = "funds_fundnavhistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds_fund.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    nav_per_unit: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    total_units: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

