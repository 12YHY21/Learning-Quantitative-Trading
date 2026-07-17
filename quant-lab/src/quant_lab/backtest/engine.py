from __future__ import annotations

from collections import defaultdict

import pandas as pd

from quant_lab.backtest.metrics import performance_metrics
from quant_lab.core.models import BacktestConfig, BacktestResult, Fill, PortfolioSnapshot, Side
from quant_lab.data.provider import DataProvider


def run_moving_average_backtest(provider: DataProvider, config: BacktestConfig) -> BacktestResult:
    """教学用日线回测：今日收盘计算信号，下一交易日开盘成交。"""
    bars = provider.bars(list(config.symbols), config.start_date, config.end_date)
    if not bars:
        raise ValueError("所选区间没有行情")
    frame = pd.DataFrame([vars(bar) for bar in bars]).sort_values(["symbol", "trading_date"])
    frame["short_ma"] = frame.groupby("symbol")["close"].transform(
        lambda value: value.rolling(config.short_window).mean()
    )
    frame["long_ma"] = frame.groupby("symbol")["close"].transform(
        lambda value: value.rolling(config.long_window).mean()
    )
    frame["signal"] = (frame["short_ma"] > frame["long_ma"]).astype(int)
    frame["target"] = frame.groupby("symbol")["signal"].shift(1).fillna(0)

    cash = config.initial_cash
    positions: dict[str, int] = defaultdict(int)
    result = BacktestResult(config=config)
    grouped = frame.groupby("trading_date", sort=True)
    for trading_date, day in grouped:
        for row in day.itertuples(index=False):
            if row.is_suspended:
                continue
            desired = 100 if row.target == 1 else 0
            change = desired - positions[row.symbol]
            if change > 0 and row.open < row.limit_up:
                price = row.open * (1 + config.slippage_rate)
                amount = price * change
                commission = max(amount * config.commission_rate, config.minimum_commission)
                if cash >= amount + commission:
                    cash -= amount + commission
                    positions[row.symbol] += change
                    result.fills.append(Fill("teaching", trading_date, row.symbol, Side.BUY, change, price, commission, 0.0))
            elif change < 0 and row.open > row.limit_down:
                quantity = -change
                price = row.open * (1 - config.slippage_rate)
                amount = price * quantity
                commission = max(amount * config.commission_rate, config.minimum_commission)
                tax = amount * config.sell_tax_rate
                cash += amount - commission - tax
                positions[row.symbol] -= quantity
                result.fills.append(Fill("teaching", trading_date, row.symbol, Side.SELL, quantity, price, commission, tax))
        close_by_symbol = {row.symbol: row.close for row in day.itertuples(index=False)}
        market_value = sum(positions[symbol] * close_by_symbol.get(symbol, 0.0) for symbol in positions)
        result.snapshots.append(PortfolioSnapshot(trading_date, cash, market_value, cash + market_value))
    result.metrics = performance_metrics([item.total_equity for item in result.snapshots])
    return result
