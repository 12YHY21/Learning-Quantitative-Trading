from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from uuid import uuid4

from quant_lab.core.models import Bar, Fill, Order, OrderStatus, Position, Side


class BrokerAdapter(ABC):
    @abstractmethod
    def submit(self, symbol: str, side: Side, quantity: int, trading_date: date,
               limit_price: float | None = None) -> Order: ...


class MockBroker(BrokerAdapter):
    def __init__(self, cash: float = 1_000_000.0, lot_size: int = 100,
                 commission_rate: float = 0.0003, minimum_commission: float = 5.0,
                 sell_tax_rate: float = 0.0005):
        self.cash = cash
        self.lot_size = lot_size
        self.commission_rate = commission_rate
        self.minimum_commission = minimum_commission
        self.sell_tax_rate = sell_tax_rate
        self.positions: dict[str, Position] = {}
        self.orders: list[Order] = []
        self.fills: list[Fill] = []

    def submit(self, symbol: str, side: Side, quantity: int, trading_date: date,
               limit_price: float | None = None) -> Order:
        order = Order(str(uuid4()), datetime.now(), trading_date, symbol, side, quantity, limit_price)
        if quantity <= 0 or quantity % self.lot_size != 0:
            order.status = OrderStatus.REJECTED
            order.reject_reason = f"数量必须是 {self.lot_size} 的正整数倍"
        self.orders.append(order)
        return order

    def settle(self) -> None:
        for position in self.positions.values():
            position.sellable_quantity = position.quantity

    def match(self, order: Order, bar: Bar) -> Fill | None:
        if order.status != OrderStatus.NEW or bar.is_suspended:
            return None
        position = self.positions.setdefault(order.symbol, Position(order.symbol))
        if order.side == Side.BUY:
            if bar.open >= (bar.limit_up or float("inf")):
                order.status, order.reject_reason = OrderStatus.REJECTED, "涨停价无法保证成交"
                return None
            if order.limit_price is not None and bar.open > order.limit_price:
                return None
            amount = bar.open * order.quantity
            commission = max(amount * self.commission_rate, self.minimum_commission)
            if amount + commission > self.cash:
                order.status, order.reject_reason = OrderStatus.REJECTED, "现金不足"
                return None
            self.cash -= amount + commission
            old_cost = position.average_cost * position.quantity
            position.quantity += order.quantity
            position.average_cost = (old_cost + amount) / position.quantity
        else:
            if order.quantity > position.sellable_quantity:
                order.status, order.reject_reason = OrderStatus.REJECTED, "违反 T+1 或可卖数量不足"
                return None
            if bar.open <= (bar.limit_down or float("-inf")):
                order.status, order.reject_reason = OrderStatus.REJECTED, "跌停价无法保证成交"
                return None
            if order.limit_price is not None and bar.open < order.limit_price:
                return None
            amount = bar.open * order.quantity
            commission = max(amount * self.commission_rate, self.minimum_commission)
            tax = amount * self.sell_tax_rate
            position.quantity -= order.quantity
            position.sellable_quantity -= order.quantity
            self.cash += amount - commission - tax
        order.status = OrderStatus.FILLED
        fill = Fill(order.order_id, bar.trading_date, order.symbol, order.side, order.quantity,
                    bar.open, commission, tax if order.side == Side.SELL else 0.0)
        self.fills.append(fill)
        return fill
