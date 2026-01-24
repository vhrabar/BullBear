from datetime import datetime
from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import (
    Integer, String, DateTime, Numeric, BigInteger,
    ForeignKey, UniqueConstraint, Index, Boolean
)

Base = declarative_base()


class UserProfile(Base):
    """Minimal stub for UserProfile to satisfy FK references."""
    __tablename__ = "users_userprofile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)


class Company(Base):
    """Minimal stub for Company to satisfy FK references."""
    __tablename__ = "trading_company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)


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
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trading_company.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    exchange: Mapped[str] = mapped_column(String(32), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserPortfolio(Base):
    """Represents one user's investment portfolio."""
    __tablename__ = "users_userportfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userprofile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=10000)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Fund(Base):
    __tablename__ = "funds_fund"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    creator_portfolio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userportfolio.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    total_units: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    nav_per_unit: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("creator_portfolio_id", "name", name="fund_creator_name_unique"),
    )


class FundHolding(Base):
    __tablename__ = "funds_fundholding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    fund_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("funds_fund.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    instrument_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    weight_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)

    __table_args__ = (
        UniqueConstraint("fund_id", "instrument_id", name="fundholding_fund_instrument_unique"),
        Index("fundholding_fund_idx", "fund_id"),
        Index("fundholding_instrument_idx", "instrument_id"),
    )


class FundNAVHistory(Base):
    __tablename__ = "funds_fundnavhistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    fund_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("funds_fund.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nav_per_unit: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    total_units: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("fundnavhistory_fund_recorded_idx", "fund_id", "recorded_at"),
    )


class Order(Base):
    """Represents a user's order intent."""
    __tablename__ = "orders_order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userprofile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    portfolio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userportfolio.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trading_instrument.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    side: Mapped[str] = mapped_column(String(4), nullable=False)  # BUY, SELL
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)  # MARKET, LIMIT, STOP, STOP_LIMIT
    time_in_force: Mapped[str] = mapped_column(String(8), nullable=False, default="GTC")

    quantity: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    limit_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=True)
    stop_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    filled_quantity: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    avg_fill_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=True)

    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    cancelled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_reason: Mapped[str] = mapped_column(String(255), nullable=True, default="")
    reject_reason: Mapped[str] = mapped_column(String(255), nullable=True, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("order_portfolio_status_idx", "portfolio_id", "status"),
        Index("order_instrument_status_idx", "instrument_id", "status"),
        Index("order_user_placed_idx", "user_id", "placed_at"),
    )


class OrderFill(Base):
    """Represents an execution (fill) against an order."""
    __tablename__ = "orders_orderfill"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders_order.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)

    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("orderfill_order_executed_idx", "order_id", "executed_at"),
    )


class PortfolioHolding(Base):
    """Links an instrument to a portfolio with quantity and cost basis."""
    __tablename__ = "trading_portfolioholding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    portfolio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userportfolio.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    average_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "instrument_id", name="portfolioholding_portfolio_instrument_unique"),
        Index("portfolioholding_portfolio_idx", "portfolio_id"),
        Index("portfolioholding_instrument_idx", "instrument_id"),
    )


class PortfolioSnapshot(Base):
    """Captures portfolio value at a point in time."""
    __tablename__ = "users_portfoliosnapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    portfolio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users_userportfolio.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    cash_balance: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=10000)
    equity_value: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=10000)
    total_value: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=10000)

    unrealized_pl: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=0)
    unrealized_pl_pct: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, default=0)

    realized_pl: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False, default=0)
    realized_pl_pct: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "ts", name="portfoliosnapshot_portfolio_ts_unique"),
        Index("portfoliosnapshot_portfolio_ts_idx", "portfolio_id", "ts"),
    )


