# 05 Python 量化研究零基础

[上一章：金融数学与统计](./04-金融数学概率与统计基础.md) ｜ [下一章：Pandas 与 SQL](./06-Pandas可视化与SQL数据管理.md)

> [!NOTE] 学习目标
> 从解释器、变量和函数学起，能读懂项目中的数据类、异常和模块；能写带输入校验的收益率程序并运行测试。

## 可点击目录

- [Python 在项目中的位置](#python-在项目中的位置)
- [解释器和虚拟环境](#解释器和虚拟环境)
- [变量类型与容器](#变量类型与容器)
- [条件与循环](#条件与循环)
- [函数和异常](#函数和异常)
- [类与数据类](#类与数据类)
- [模块和项目目录](#模块和项目目录)
- [完整练习程序](#完整练习程序)
- [pytest 与排错](#pytest-与排错)
- [自测题](#自测题)

## Python 在项目中的位置

Python 负责读取数据、计算指标、运行策略、更新账本、保存结果、提供 FastAPI 和编写测试。浏览器前端使用 JavaScript，但交易规则全部在 Python 后端。

## 解释器和虚拟环境

```powershell
Set-Location <仓库目录>\quant-lab
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

- `-m venv` 创建隔离环境；
- 激活脚本让当前终端使用环境内 Python；
- `pip install -e` 以可编辑模式安装项目；
- `.[dev]` 同时安装 pytest 等开发依赖。

## 变量、类型与容器

```python
symbol = "600001.SH"      # str
price = 10.20             # float
quantity = 100            # int
is_suspended = False      # bool
nothing = None            # 暂无值

symbols = ["600001.SH", "000001.SZ"]
prices = {"600001.SH": 10.20, "000001.SZ": 12.10}
```

变量是名称，对象保存值。列表保持顺序，字典按键查值。浮点数存在二进制近似误差，测试应使用近似比较。

## 条件与循环

```python
if is_suspended:
    print("今日不可交易")
elif quantity % 100 != 0:
    print("数量不符合教学整手规则")
else:
    print("进入订单校验")

for symbol in symbols:
    print(symbol)
```

缩进决定代码块。`%` 是取余。循环适合逐项逻辑；大型表格数值计算后续使用 Pandas 向量化。

## 函数和异常

```python
def simple_return(start_price: float, end_price: float) -> float:
    """计算单期简单收益率。"""
    if start_price <= 0:
        raise ValueError("初始价格必须大于 0")
    return end_price / start_price - 1
```

- 参数后的 `float` 是类型提示；
- `-> float` 表示预期返回类型；
- `raise` 主动报告非法输入；
- `return` 把结果交回调用者。

类型提示不会自动拒绝负价格，业务校验仍需显式编写。

```python
try:
    value = simple_return(0, 10)
except ValueError as error:
    print("计算失败：", error)
```

不要使用空的 `except Exception: pass`，否则数据错误会伪装成正常结果。

## 类与数据类

```python
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Bar:
    trading_date: date
    symbol: str
    open: float
    close: float

bar = Bar(date(2025, 1, 2), "600001.SH", 10.0, 10.2)
print(bar.symbol, bar.close)
```

类是对象的结构说明。`frozen=True` 让实例创建后不能随意改字段，降低历史事实被篡改的风险。

## 模块和项目目录

```text
quant-lab
├─ pyproject.toml
├─ data
├─ src
│  └─ quant_lab
│     ├─ core
│     ├─ data
│     ├─ backtest
│     ├─ paper
│     └─ api
└─ tests
```

`from quant_lab.core.models import Bar` 表示从已安装包的模块导入 Bar。

## 完整练习程序

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Trade:
    symbol: str
    buy_price: float
    sell_price: float
    quantity: int

def trade_profit(trade: Trade, fee: float) -> float:
    if trade.buy_price <= 0 or trade.sell_price <= 0:
        raise ValueError("价格必须大于 0")
    if trade.quantity <= 0:
        raise ValueError("数量必须大于 0")
    gross = (trade.sell_price - trade.buy_price) * trade.quantity
    return gross - fee

trade = Trade("600001.SH", 10.0, 10.5, 100)
print("扣费后盈利：", trade_profit(trade, fee=10.0))
```

手算毛盈利 50 元，扣费 10 元，净盈利 40 元。

## pytest 与排错

```python
import pytest

def test_simple_return():
    assert simple_return(10, 11) == pytest.approx(0.10)

def test_invalid_start_price():
    with pytest.raises(ValueError):
        simple_return(0, 11)
```

第一条验证正常结果，第二条验证失败分支。

若出现 `ModuleNotFoundError`，确认已激活虚拟环境并执行 `pip install -e ".[dev]"`。若 PowerShell 禁止激活，可直接运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

> [!IMPORTANT] 量化重点
> 参数、返回值、异常和状态要明确。让错误尽早失败，比返回一个看似正常的 0 更安全。

## 本章总结

- 虚拟环境隔离依赖。
- 类型提示不替代业务校验。
- 函数封装输入、处理和输出。
- 异常让非法状态可见。
- 数据类表达稳定领域对象。
- pytest 同时验证成功和失败路径。

## 自测题

1. `quantity % 100 != 0` 检查什么？
2. 为什么类型提示不能替代正数校验？
3. `frozen=True` 对行情对象有什么帮助？
4. 静默吞掉异常有什么风险？

<details>
<summary>展开参考答案</summary>

1. 数量是否不能被 100 整除。
2. 正数和负数都可能是 float，业务范围仍需校验。
3. 防止历史行情被意外原地修改。
4. 会隐藏故障，让错误数据继续进入回测。

</details>

## 零基础调试法：让程序把思考过程说出来

初学者最容易把报错当成失败。实际上，报错是程序告诉你哪条假设不成立。

```python
def calculate_order_value(price: float, quantity: int) -> float:
    print("收到价格:", price)
    print("收到数量:", quantity)
    if price <= 0:
        raise ValueError("price 必须大于 0")
    if quantity <= 0:
        raise ValueError("quantity 必须大于 0")
    value = price * quantity
    print("订单金额:", value)
    return value

assert calculate_order_value(10.5, 100) == 1050.0
```

掌握后用日志替代随意 `print`，但排查顺序仍相同：

1. 输入的类型和值是什么？
2. 条件分支走了哪一条？
3. 循环处理到哪个证券和日期？
4. 函数输出是否满足业务不变量？
5. 错误是数据问题、代码问题还是规则假设问题？

### 类型正确不代表业务正确

```python
def validate_weight(weight: float) -> None:
    if not 0.0 <= weight <= 1.0:
        raise ValueError("不允许杠杆时，权重必须在 0 到 1 之间")
```

`1.5` 是合法的 float，却可能是非法的无杠杆权重。

> [!TIP] 工程验收
> 每个核心函数至少有一个正常测试、一个边界测试和一个失败测试；异常信息应告诉初学者“哪个输入为什么不合法”。

### 小练习

为订单数量函数补充三个测试：100 股通过、150 股拒绝、0 股拒绝。不要在函数内部用 `except Exception: pass` 吞掉错误。
