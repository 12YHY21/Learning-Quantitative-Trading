from datetime import date
from pathlib import Path

from quant_lab.core.strategy import MovingAverageStrategy
from quant_lab.data.provider import CsvDataProvider


DATA = Path(__file__).parents[1] / "data"


def test_fundamentals_respect_available_date():
    provider = CsvDataProvider(DATA)
    before_annual_report = provider.fundamentals(["600001.SH"], date(2025, 2, 1))
    after_annual_report = provider.fundamentals(["600001.SH"], date(2025, 4, 1))
    assert len(before_annual_report) == 1
    assert len(after_annual_report) == 2


def test_strategy_starts_after_long_window():
    provider = CsvDataProvider(DATA)
    bars = provider.bars(["600001.SH"], date(2025, 1, 2), date(2025, 1, 17))
    signals = MovingAverageStrategy(3, 5).generate_signals(bars)
    assert len(signals) == len(bars) - 4
    assert signals[0].trading_date == date(2025, 1, 8)
