from fastapi.testclient import TestClient

from quant_lab.api.app import app


client = TestClient(app)


def test_health_and_backtest():
    assert client.get("/health").json()["mode"] == "research-and-paper-only"
    response = client.post("/backtests", json={
        "symbols": ["600001.SH"], "start_date": "2025-01-02", "end_date": "2025-01-17",
        "short_window": 3, "long_window": 5,
    })
    assert response.status_code == 201
    assert len(response.json()["equity"]) == 12
    saved = client.get(f"/backtests/{response.json()['id']}")
    assert saved.status_code == 200
    assert saved.json()["config"]["symbols"] == ["600001.SH"]


def test_rejects_invalid_windows():
    response = client.post("/backtests", json={
        "symbols": ["600001.SH"], "start_date": "2025-01-02", "end_date": "2025-01-17",
        "short_window": 5, "long_window": 3,
    })
    assert response.status_code == 422


def test_paper_order_and_portfolio():
    rejected = client.post("/orders", json={
        "symbol": "600001.SH", "side": "buy", "quantity": 50,
        "trading_date": "2025-01-02",
    })
    assert rejected.status_code == 201
    assert rejected.json()["order"]["status"] == "rejected"
    filled = client.post("/orders", json={
        "symbol": "600001.SH", "side": "buy", "quantity": 100,
        "trading_date": "2025-01-02",
    })
    assert filled.json()["order"]["status"] == "filled"
    portfolio = client.get("/portfolio").json()
    assert portfolio["mode"] == "paper"
    assert portfolio["positions"][0]["quantity"] == 100


def test_built_frontend_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "<div id=\"app\"></div>" in response.text
