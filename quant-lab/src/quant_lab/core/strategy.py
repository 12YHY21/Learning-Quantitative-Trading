from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from quant_lab.core.models import Bar, Signal


class Strategy(Protocol):
    """策略只读取已知行情并产生判断，不修改账户。"""

    def generate_signals(self, bars: list[Bar]) -> list[Signal]: ...


@dataclass(frozen=True)
class MovingAverageStrategy:
    short_window: int = 3
    long_window: int = 5

    def __post_init__(self) -> None:
        if self.short_window <= 0 or self.short_window >= self.long_window:
            raise ValueError("必须满足 0 < short_window < long_window")

    def generate_signals(self, bars: list[Bar]) -> list[Signal]:
        frame = pd.DataFrame([vars(item) for item in bars]).sort_values(["symbol", "trading_date"])
        if frame.empty:
            return []
        frame["short_ma"] = frame.groupby("symbol")["close"].transform(
            lambda value: value.rolling(self.short_window).mean()
        )
        frame["long_ma"] = frame.groupby("symbol")["close"].transform(
            lambda value: value.rolling(self.long_window).mean()
        )
        ready = frame.dropna(subset=["short_ma", "long_ma"])
        return [Signal(
            trading_date=row.trading_date, symbol=row.symbol,
            score=1.0 if row.short_ma > row.long_ma else -1.0,
            reason=f"MA{self.short_window}={row.short_ma:.4f}, MA{self.long_window}={row.long_ma:.4f}",
        ) for row in ready.itertuples(index=False)]
