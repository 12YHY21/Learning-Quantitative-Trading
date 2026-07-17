from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

import pandas as pd

from quant_lab.core.models import Bar, CorporateAction, FundamentalRecord, Instrument


class DataProvider(ABC):
    @abstractmethod
    def instruments(self) -> list[Instrument]: ...

    @abstractmethod
    def trading_calendar(self, start: date, end: date) -> list[date]: ...

    @abstractmethod
    def bars(self, symbols: list[str], start: date, end: date) -> list[Bar]: ...

    @abstractmethod
    def corporate_actions(self, symbols: list[str], start: date, end: date) -> list[CorporateAction]: ...

    @abstractmethod
    def fundamentals(self, symbols: list[str], available_on: date) -> list[FundamentalRecord]: ...


class CsvDataProvider(DataProvider):
    """把第三方字段隔离在 CSV 适配器中，策略层只接触统一领域对象。"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def instruments(self) -> list[Instrument]:
        frame = pd.read_csv(self.data_dir / "instruments.csv")
        return [
            Instrument(
                symbol=row.symbol,
                name=row.name,
                exchange=row.exchange,
                board=row.board,
                list_date=date.fromisoformat(row.list_date),
                lot_size=int(row.lot_size),
            )
            for row in frame.itertuples(index=False)
        ]

    def trading_calendar(self, start: date, end: date) -> list[date]:
        frame = pd.read_csv(self.data_dir / "bars.csv", parse_dates=["date"])
        dates = sorted({value.date() for value in frame["date"]})
        return [value for value in dates if start <= value <= end]

    def bars(self, symbols: list[str], start: date, end: date) -> list[Bar]:
        frame = pd.read_csv(self.data_dir / "bars.csv", parse_dates=["date"])
        frame = frame[
            frame["symbol"].isin(symbols)
            & (frame["date"].dt.date >= start)
            & (frame["date"].dt.date <= end)
        ].sort_values(["date", "symbol"])
        return [
            Bar(
                trading_date=row.date.date(), symbol=row.symbol,
                open=float(row.open), high=float(row.high), low=float(row.low),
                close=float(row.close), volume=int(row.volume),
                is_suspended=bool(row.is_suspended),
                limit_up=float(row.limit_up), limit_down=float(row.limit_down),
            )
            for row in frame.itertuples(index=False)
        ]

    def corporate_actions(self, symbols: list[str], start: date, end: date) -> list[CorporateAction]:
        frame = pd.read_csv(self.data_dir / "corporate_actions.csv", parse_dates=["ex_date"])
        frame = frame[
            frame["symbol"].isin(symbols)
            & (frame["ex_date"].dt.date >= start)
            & (frame["ex_date"].dt.date <= end)
        ].sort_values(["ex_date", "symbol"])
        return [CorporateAction(
            symbol=row.symbol, ex_date=row.ex_date.date(), action_type=row.action_type,
            cash_dividend=float(row.cash_dividend), split_ratio=float(row.split_ratio),
        ) for row in frame.itertuples(index=False)]

    def fundamentals(self, symbols: list[str], available_on: date) -> list[FundamentalRecord]:
        frame = pd.read_csv(
            self.data_dir / "fundamentals.csv", parse_dates=["report_date", "available_date"]
        )
        frame = frame[
            frame["symbol"].isin(symbols)
            & (frame["available_date"].dt.date <= available_on)
        ].sort_values(["symbol", "available_date"])
        return [FundamentalRecord(
            symbol=row.symbol, report_date=row.report_date.date(),
            available_date=row.available_date.date(), revenue=float(row.revenue),
            net_income=float(row.net_income), equity=float(row.equity),
        ) for row in frame.itertuples(index=False)]
