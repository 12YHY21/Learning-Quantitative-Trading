# 06 Pandas、可视化与 SQL 数据管理

[上一章：Python 零基础](./05-Python量化研究零基础.md) ｜ [下一章：A 股数据与点时股票池](./07-A股数据源交易日历与时点股票池.md)

> [!NOTE] 学习目标
> 能读取、排序、筛选和分组行情；理解滚动窗口和日期对齐；能用图表发现异常；能设计带唯一约束的行情表并理解事务。

## 可点击目录

- [Series 与 DataFrame](#series-与-dataframe)
- [读取并检查行情](#读取并检查行情)
- [排序筛选与分组](#排序筛选与分组)
- [滚动窗口与时间对齐](#滚动窗口与时间对齐)
- [缺失值处理](#缺失值处理)
- [可视化是检查工具](#可视化是检查工具)
- [SQL 索引与事务](#sql索引与事务)
- [完整数据实践](#完整数据实践)
- [失败路径与自测](#失败路径与自测)

## Series 与 DataFrame

Series 是带索引的一维序列，DataFrame 是行列都有标签的二维表。索引不是装饰：两个 Series 运算时默认按标签对齐。

```python
import pandas as pd

prices = pd.Series(
    [10.0, 10.2, 10.4],
    index=pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]),
    name="close",
)
print(prices)
```

## 读取并检查行情

```python
from pathlib import Path
import pandas as pd

bars = pd.read_csv(
    Path("E:/Study/quant-lab/data/bars.csv"),
    parse_dates=["date"],
)

print(bars.head())
print(bars.dtypes)
print(bars.shape)
print(bars.isna().sum())
print(bars.duplicated(["symbol", "date"]).sum())
```

检查字段和值、数据类型、行列数量、缺失和业务键重复。不要读完文件就直接回测。

## 排序、筛选与分组

```python
bars = bars.sort_values(["symbol", "date"])

stock = bars.loc[
    bars["symbol"].eq("600001.SH"),
    ["date", "open", "close", "volume"],
]

summary = bars.groupby("symbol").agg(
    first_date=("date", "min"),
    last_date=("date", "max"),
    observations=("close", "count"),
    average_volume=("volume", "mean"),
)
print(summary)
```

时间序列计算前必须排序。`groupby` 先拆组，`agg` 再计算每组汇总。

## 滚动窗口与时间对齐

三日均线：

$$
MA_{3,t}=\frac{P_t+P_{t-1}+P_{t-2}}{3}
$$

```python
bars["ma3"] = bars.groupby("symbol")["close"].transform(
    lambda values: values.rolling(3).mean()
)

bars["raw_signal"] = (bars["close"] > bars["ma3"]).astype(int)
bars["next_open_target"] = bars.groupby("symbol")["raw_signal"].shift(1)
```

`transform` 返回与原表等长结果。每只股票最初两行均线缺失，因为窗口不足。`shift(1)` 让今日收盘信号只在下一行使用，避免用收盘信息按同日开盘成交。

## 缺失值处理

缺失可能来自新股上市前、停牌、指标窗口不足、数据源故障或字段不适用。不同原因不能统一 `fillna(0)`。

| 原因 | 常见处理 |
|---|---|
| 窗口不足 | 保留缺失，不产生信号 |
| 停牌 | 标记不可交易 |
| 数据源故障 | 整批失败并报警 |
| 确实为 0 | 保存 0 并保留来源 |
| 不适用 | 保留缺失或分类标记 |

## 可视化是检查工具

```python
stock = bars[bars["symbol"].eq("600001.SH")].set_index("date")
stock[["close", "ma3"]].plot(
    title="教学股票收盘价与三日均线",
    grid=True,
)
```

图表用于发现跳价、停牌成交量、回撤和集中度。先检查表格，再看图；漂亮曲线不能修复错误索引。

## SQL、索引与事务

CSV 简单，但难以保证唯一性、原子写入和高效查询。行情表可以设计为：

```sql
CREATE TABLE bars (
    symbol TEXT NOT NULL,
    trading_date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    PRIMARY KEY (symbol, trading_date)
);
```

复合主键防止重复日线。索引加速部分查询，却增加空间和写入成本，不能说“索引永远更快”。

事务让一组写入要么全部成功，要么失败回滚：

```python
import sqlite3

connection = sqlite3.connect(":memory:")
try:
    connection.execute("BEGIN")
    connection.execute(
        "CREATE TABLE bars(symbol TEXT, date TEXT, close REAL, "
        "UNIQUE(symbol, date))"
    )
    connection.execute(
        "INSERT INTO bars VALUES (?, ?, ?)",
        ("600001.SH", "2025-01-02", 10.2),
    )
    connection.commit()
except Exception:
    connection.rollback()
    raise
```

参数占位符 `?` 避免拼接 SQL，也降低注入风险。

## 完整数据实践

```python
from pathlib import Path
import sqlite3
import pandas as pd

bars = pd.read_csv(
    Path("E:/Study/quant-lab/data/bars.csv"),
    parse_dates=["date"],
).sort_values(["symbol", "date"])

if bars.duplicated(["symbol", "date"]).any():
    raise ValueError("发现重复日线")

bars["return"] = bars.groupby("symbol")["close"].pct_change()
bars["ma3"] = bars.groupby("symbol")["close"].transform(
    lambda values: values.rolling(3).mean()
)

connection = sqlite3.connect(":memory:")
bars.to_sql("bars", connection, index=False, if_exists="fail")

result = pd.read_sql_query(
    """
    SELECT symbol, COUNT(*) AS observations, AVG(close) AS avg_close
    FROM bars
    GROUP BY symbol
    ORDER BY symbol
    """,
    connection,
)
print(result)
```

链路是 CSV → 校验 → 计算 → SQLite → SQL 查询。内存数据库不会修改真实数据。

## 失败路径与自测

- `KeyError: 'close'`：打印 `bars.columns.tolist()` 检查字段。
- 滚动结果跨股票：检查是否分组并排序。
- SQL 重复键失败：保留约束，先定位重复来源。
- 图表日期乱序：检查日期类型和排序。

> [!WARNING] 回测陷阱
> 对整表先用未来数据填充，再切训练集，会把未来泄漏到历史。填充必须按证券和时间方向说明依据。

## 本章总结

- DataFrame 用标签表达证券、日期和字段。
- 时间序列计算前必须排序和分组。
- 窗口初期缺失是正常信息边界。
- 可视化用于发现问题，不用于证明策略。
- SQL 唯一约束和事务保护一致性。

## 自测题

1. 为什么不能直接对多股票表调用 `close.rolling(3)`？
2. `shift(1)` 解决什么问题？
3. 为什么停牌缺失不能填 0？
4. 复合主键防止什么错误？

<details>
<summary>展开参考答案</summary>

1. 窗口会跨证券边界。
2. 让收盘信号只在下一时点使用。
3. 0 有具体含义，不能代表不可交易或未知。
4. 防止同一证券同一日期重复。

</details>

## 零基础数据流推演：一行行情怎样进入数据库

以 `2025-01-02,600000.SH,10.00,10.20,9.90,10.10,100000` 为例：

1. `read_csv` 把文本读入 DataFrame。
2. `parse_dates` 把日期转换为 Timestamp。
3. `dtype` 保证证券代码保持字符串。
4. 质量检查验证 OHLC 和成交量。
5. 复合主键验证证券与日期不重复。
6. 事务把合格行写入数据库。
7. 查询按证券和日期排序返回研究层。

```python
required = ["symbol", "date", "open", "high", "low", "close", "volume"]
missing = set(required) - set(bars.columns)
if missing:
    raise ValueError(f"缺少字段: {sorted(missing)}")

if bars.duplicated(["symbol", "date"]).any():
    raise ValueError("发现重复的证券-日期键")

invalid = (
    (bars["high"] < bars[["open", "close", "low"]].max(axis=1))
    | (bars["low"] > bars[["open", "close", "high"]].min(axis=1))
)
if invalid.any():
    raise ValueError("OHLC 关系不合法")
```

### 为什么要保留长表

行情长表每行是一只证券的一天，便于新增证券、按证券分组和数据库存储。因子研究有时会透视为“日期 × 证券”宽表，但完成运算后要清楚索引和列分别代表什么。

### 图表与 SQL 的共同原则

- 图表用于发现异常，不用于掩盖缺失。
- SQL 查询必须有稳定排序，否则“前一行”没有时间含义。
- 写入使用事务，避免只写入一半。
- 数据变更记录版本，不直接覆盖原始快照。

> [!CAUTION] 回测陷阱
> `groupby().rolling()` 前若未按证券和日期排序，窗口可能在错误时间顺序上计算；代码能运行，结果仍可能错误。
