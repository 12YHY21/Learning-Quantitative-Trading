# Quant Lab 教学平台

这是《中国 A 股量化交易与金融百科教程》的配套项目，只支持离线研究、回测和模拟盘，不连接券商，不发送真实订单。

教程入口：[00｜完整教程索引与学习路线](../docs/00-完整教程索引与学习路线.md)。

后端全部使用 Python 3.12、FastAPI、Pandas、NumPy、SQLAlchemy、SQLite 和 pytest，不使用 Java、Spring、Maven 或 Gradle。`frontend/` 中的 Vue 3 与 ECharts 只负责浏览器界面。

## 目录

```text
quant-lab/
├─ data/                 # 离线教学数据
├─ src/quant_lab/        # Python 后端
├─ tests/                # pytest
├─ frontend/             # Vue 3 / ECharts
└─ pyproject.toml
```

## Windows 启动

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

Set-Location frontend
corepack enable
pnpm install --frozen-lockfile
pnpm run build
Set-Location ..

uvicorn quant_lab.api.app:app --reload
```

打开 `http://127.0.0.1:8000/docs` 查看接口，打开 `http://127.0.0.1:8000/` 查看教学面板。

## 测试

```powershell
pytest -q
```

## 项目边界

- `BrokerAdapter` 只是领域抽象。
- 只实现 `MockBroker`，不包含真实券商 SDK。
- 行情、财务、费用和成交结果都是教学数据或教学参数。
- 不构成投资建议，也不代表任何市场或券商的真实结果。
