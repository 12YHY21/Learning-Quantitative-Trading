from __future__ import annotations

import math

import numpy as np


def performance_metrics(equity: list[float], annual_days: int = 252) -> dict[str, float]:
    if len(equity) < 2 or equity[0] <= 0:
        return {"total_return": 0.0, "annualized_return": 0.0, "volatility": 0.0,
                "sharpe": 0.0, "max_drawdown": 0.0}
    values = np.asarray(equity, dtype=float)
    returns = values[1:] / values[:-1] - 1
    total_return = values[-1] / values[0] - 1
    annualized_return = (values[-1] / values[0]) ** (annual_days / len(returns)) - 1
    volatility = float(np.std(returns, ddof=1) * math.sqrt(annual_days)) if len(returns) > 1 else 0.0
    sharpe = float(np.mean(returns) / np.std(returns, ddof=1) * math.sqrt(annual_days)) if len(returns) > 1 and np.std(returns, ddof=1) > 0 else 0.0
    peaks = np.maximum.accumulate(values)
    max_drawdown = float(np.min(values / peaks - 1))
    return {
        "total_return": float(total_return),
        "annualized_return": float(annualized_return),
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
    }
