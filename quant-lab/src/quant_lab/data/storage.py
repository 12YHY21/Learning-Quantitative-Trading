from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import Column, Integer, MetaData, String, Table, Text, create_engine, select


class BacktestStore:
    """用 SQLite 保存可重放的回测请求与结果 JSON。"""

    def __init__(self, database_path: Path):
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{database_path}")
        self.metadata = MetaData()
        self.results = Table(
            "backtest_results", self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("strategy", String(64), nullable=False),
            Column("payload", Text, nullable=False),
        )
        self.metadata.create_all(self.engine)

    def save(self, payload: dict, strategy: str = "moving-average") -> dict:
        with self.engine.begin() as connection:
            result = connection.execute(
                self.results.insert().values(strategy=strategy, payload=json.dumps(payload, ensure_ascii=False))
            )
            result_id = int(result.inserted_primary_key[0])
        return {"id": result_id, **payload}

    def get(self, result_id: int) -> dict | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                select(self.results.c.payload).where(self.results.c.id == result_id)
            ).first()
        return {"id": result_id, **json.loads(row.payload)} if row else None
