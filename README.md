# Learning Quantitative Trading

一套面向零基础读者的中国 A 股量化交易教程，以及配套的本地 Web 研究、回测与模拟盘平台。

> [!WARNING]
> 本仓库只用于金融知识、量化研究、历史回测和模拟盘教学，不构成投资建议，不承诺收益，不连接真实券商，也不会发送真实订单。

## 仓库内容

| 目录 | 内容 |
|---|---|
| `docs/` | 00～18 共 19 章中文教程 |
| `quant-lab/` | Python 量化研究平台 |
| `scripts/` | 仓库文档静态检查 |
| `DATA_SOURCES.md` | 教学数据说明与授权边界 |

从 [00｜完整教程索引与学习路线](./docs/00-完整教程索引与学习路线.md) 开始学习。

## 学习路线

1. 01～06：金融、A 股市场、数学、Python、Pandas 与 SQL。
2. 07～10：数据源、历史股票池、复权、偏差和研究假设。
3. 11～16：向量化回测、事件驱动回测、绩效、因子、策略和机器学习。
4. 17～18：Python 后端、Vue 前端、模拟盘、测试和综合验收。

每章包含零基础解释、公式手算、可运行代码、Mermaid 图、失败路径、排错、自测题和工程验收。

## Quant Lab

后端全部使用 Python 3.12、FastAPI、Pandas、NumPy、SQLAlchemy、SQLite 和 pytest；前端使用 Vue 3 与 ECharts。项目不包含 Java、Spring、Maven、Gradle 或真实券商 SDK。

### Windows 启动

```powershell
Set-Location quant-lab
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

打开：

- `http://127.0.0.1:8000/`：教学面板。
- `http://127.0.0.1:8000/docs`：OpenAPI 接口文档。

更多信息见 [Quant Lab 说明](./quant-lab/README.md)。

## 验证

```powershell
python scripts/validate_docs.py

Set-Location quant-lab
pytest -q

Set-Location frontend
pnpm install --frozen-lockfile
pnpm run build
```

GitHub Actions 会自动执行文档检查、Python 测试和前端构建。

## 数据说明

仓库中的 CSV 是小型确定性教学数据，不是完整真实市场数据，不能用于评价策略长期有效性。具体字段、区间和用途见 [DATA_SOURCES.md](./DATA_SOURCES.md)。

## 授权

- `quant-lab/` 与 `scripts/` 中的代码使用 [MIT License](./LICENSE-CODE)。
- `docs/` 中的教程使用 [Creative Commons Attribution 4.0 International](./LICENSE-DOCS.md)。
- 教学数据的使用说明见 [DATA_SOURCES.md](./DATA_SOURCES.md)。

第三方名称、链接和规则文本的权利归各自权利人所有。
