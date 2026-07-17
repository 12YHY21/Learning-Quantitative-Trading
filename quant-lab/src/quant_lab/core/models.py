from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(StrEnum):
    NEW = "new"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Instrument:
    symbol: str
    name: str
    exchange: str
    board: str
    list_date: date
    lot_size: int = 100


@dataclass(frozen=True)
class Bar:
    trading_date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    is_suspended: bool = False
    limit_up: float | None = None
    limit_down: float | None = None


@dataclass(frozen=True)
class CorporateAction:
    symbol: str
    ex_date: date
    action_type: str
    cash_dividend: float = 0.0
    split_ratio: float = 1.0


@dataclass(frozen=True)
class FundamentalRecord:
    symbol: str
    report_date: date
    available_date: date
    revenue: float
    net_income: float
    equity: float


@dataclass(frozen=True)
class Signal:
    trading_date: date
    symbol: str
    score: float
    reason: str


@dataclass(frozen=True)
class TargetPosition:
    trading_date: date
    symbol: str
    target_weight: float


@dataclass
class Order:
    order_id: str
    created_at: datetime
    trading_date: date
    symbol: str
    side: Side
    quantity: int
    limit_price: float | None = None
    status: OrderStatus = OrderStatus.NEW
    reject_reason: str | None = None


@dataclass(frozen=True)
class Fill:
    order_id: str
    trading_date: date
    symbol: str
    side: Side
    quantity: int
    price: float
    commission: float
    tax: float


@dataclass
class Position:
    symbol: str
    quantity: int = 0
    sellable_quantity: int = 0
    average_cost: float = 0.0


@dataclass(frozen=True)
class PortfolioSnapshot:
    trading_date: date
    cash: float
    market_value: float
    total_equity: float


@dataclass(frozen=True)
class BacktestConfig:
    symbols: tuple[str, ...]
    start_date: date
    end_date: date
    initial_cash: float = 1_000_000.0
    short_window: int = 3
    long_window: int = 5
    commission_rate: float = 0.0003
    minimum_commission: float = 5.0
    sell_tax_rate: float = 0.0005
    slippage_rate: float = 0.0002


@dataclass
class BacktestResult:
    config: BacktestConfig
    snapshots: list[PortfolioSnapshot] = field(default_factory=list)
    fills: list[Fill] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
