from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from quant_lab.backtest.engine import run_moving_average_backtest
from quant_lab.core.models import BacktestConfig, Side
from quant_lab.data.provider import CsvDataProvider
from quant_lab.data.storage import BacktestStore
from quant_lab.paper.broker import MockBroker

PROJECT_ROOT = Path(__file__).resolve().parents[3]
provider = CsvDataProvider(PROJECT_ROOT / "data")
app = FastAPI(title="Quant Lab 教学 API", version="0.1.0")
store = BacktestStore(PROJECT_ROOT / "data" / "quant_lab.db")
broker = MockBroker()
last_order_date: date | None = None
frontend_dist = PROJECT_ROOT / "frontend" / "dist"
if (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="frontend-assets")


class BacktestRequest(BaseModel):
    symbols: list[str] = Field(min_length=1)
    start_date: date
    end_date: date
    initial_cash: float = Field(default=1_000_000, gt=0)
    short_window: int = Field(default=3, ge=1, le=60)
    long_window: int = Field(default=5, ge=2, le=250)


class OrderRequest(BaseModel):
    symbol: str
    side: Side
    quantity: int = Field(gt=0)
    trading_date: date
    limit_price: float | None = Field(default=None, gt=0)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    page = frontend_dist / "index.html"
    if not page.exists():
        page = PROJECT_ROOT / "frontend" / "index.html"
    return page.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "research-and-paper-only"}


@app.get("/instruments")
def instruments() -> list[dict]:
    return [vars(item) for item in provider.instruments()]


@app.get("/bars")
def bars(symbol: str, start_date: date, end_date: date) -> list[dict]:
    if start_date > end_date:
        raise HTTPException(422, "start_date 不能晚于 end_date")
    return [vars(item) for item in provider.bars([symbol], start_date, end_date)]


@app.get("/strategies")
def strategies() -> list[dict]:
    return [{"id": "moving-average", "name": "双均线教学策略", "live_trading": False}]


@app.post("/backtests", status_code=201)
def create_backtest(request: BacktestRequest) -> dict:
    if request.short_window >= request.long_window:
        raise HTTPException(422, "短均线窗口必须小于长均线窗口")
    config = BacktestConfig(tuple(request.symbols), request.start_date, request.end_date,
                            request.initial_cash, request.short_window, request.long_window)
    try:
        result = run_moving_average_backtest(provider, config)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    payload = {
        "config": jsonable_encoder(config),
        "metrics": result.metrics,
        "equity": jsonable_encoder(result.snapshots),
        "fills": jsonable_encoder(result.fills),
    }
    return store.save(payload)


@app.get("/backtests/{result_id}")
def get_backtest(result_id: int) -> dict:
    payload = store.get(result_id)
    if payload is None:
        raise HTTPException(404, "回测不存在")
    return payload


@app.get("/orders")
def orders() -> list[dict]:
    return jsonable_encoder(broker.orders)


@app.post("/orders", status_code=201)
def submit_order(request: OrderRequest) -> dict:
    global last_order_date
    if last_order_date is not None and request.trading_date > last_order_date:
        broker.settle()
    last_order_date = max(last_order_date, request.trading_date) if last_order_date else request.trading_date
    bars = provider.bars([request.symbol], request.trading_date, request.trading_date)
    if not bars:
        raise HTTPException(404, "该证券在指定日期没有教学行情")
    order = broker.submit(request.symbol, request.side, request.quantity,
                          request.trading_date, request.limit_price)
    fill = broker.match(order, bars[0])
    return {"order": jsonable_encoder(order), "fill": jsonable_encoder(fill)}


@app.get("/portfolio")
def portfolio() -> dict:
    return {"cash": broker.cash, "positions": jsonable_encoder(list(broker.positions.values())),
            "mode": "paper"}
