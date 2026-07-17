from datetime import date

from quant_lab.core.models import Bar, OrderStatus, Side
from quant_lab.paper.broker import MockBroker


BAR = Bar(date(2025, 1, 2), "600001.SH", 10, 10.3, 9.9, 10.2, 10000, False, 11, 9)


def test_lot_size_and_t_plus_one():
    broker = MockBroker(cash=100_000)
    invalid = broker.submit(BAR.symbol, Side.BUY, 50, BAR.trading_date)
    assert invalid.status == OrderStatus.REJECTED
    buy = broker.submit(BAR.symbol, Side.BUY, 100, BAR.trading_date)
    assert broker.match(buy, BAR) is not None
    sell_same_day = broker.submit(BAR.symbol, Side.SELL, 100, BAR.trading_date)
    assert broker.match(sell_same_day, BAR) is None
    assert sell_same_day.reject_reason.startswith("违反 T+1")
    broker.settle()
    sell_next_day = broker.submit(BAR.symbol, Side.SELL, 100, date(2025, 1, 3))
    assert broker.match(sell_next_day, BAR) is not None
