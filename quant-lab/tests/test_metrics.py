import pytest

from quant_lab.backtest.metrics import performance_metrics


def test_total_return_and_drawdown():
    metrics = performance_metrics([100.0, 110.0, 99.0, 120.0])
    assert metrics["total_return"] == pytest.approx(0.20)
    assert metrics["max_drawdown"] == pytest.approx(-0.10)


def test_short_series_is_safe():
    assert performance_metrics([100.0])["total_return"] == 0.0
