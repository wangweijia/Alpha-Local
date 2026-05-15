# Alpha-Local

一个基于 **FastAPI + Jinja2 + Vue3（本地静态资源集成）** 的单体化本地投资辅助系统示例。项目把页面渲染、技能 API、SQLite 存储与定时任务收敛在同一个 Python 服务里，适合作为本地原型、课程示例或轻量级内部工具的起点。

## 项目特点

- **单体架构，开箱即跑**：后端页面、API、数据库、定时任务都在同一个服务中。
- **本地数据库存储**：默认使用 SQLite，本地启动时会自动初始化数据库文件。
- **默认内置 Mock 持仓数据**：即使没有接入真实行情 / 券商 SDK，也可以直接看到界面效果。
- **支持后续接入 EmQuant SDK**：`core/emquant_client.py` 已预留真实持仓获取逻辑。
- **带有定时任务**：
  - 每 10 分钟自动同步一次持仓
  - 每个工作日 14:30 生成一次尾盘建议
- **自带前端页面**：启动后可直接访问 dashboard，无需额外单独启动前端工程。

---

## 目录结构

```text
Alpha-Local/
├── api/                 # Skill API 路由
├── core/                # AI、持仓同步、组合计算等核心逻辑
├── models/              # 数据库配置与实体定义
├── static/              # 前端静态资源
├── templates/           # Jinja2 页面模板
├── tests/               # 测试代码
├── main.py              # FastAPI 应用入口
├── requirements.txt     # Python 依赖
└── README.md
```

---

## 环境要求

建议使用以下环境：

- Python **3.10+**（推荐 3.11）
- pip 最新版本
- 操作系统：macOS / Linux / Windows 均可

可先确认 Python 版本：

```bash
python --version
```

如果你的系统同时装了多个 Python，也可以使用：

```bash
python3 --version
```

---

## 初始化步骤

### 1）克隆项目

```bash
git clone https://github.com/wangweijia/Alpha-Local.git
cd Alpha-Local
```

### 2）创建虚拟环境（推荐）

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

激活成功后，命令行前面通常会出现 `(.venv)`。

### 3）安装依赖

```bash
pip install -r requirements.txt
```

当前核心依赖包括：

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `jinja2`
- `apscheduler`
- `httpx`

### 4）初始化数据库

本项目**不需要手动执行建表脚本**。应用启动时会自动完成：

- 数据库引擎初始化
- 表结构创建
- 持仓种子数据写入（首次启动时）

默认数据库文件位置：

```text
alpha_local.db
```

该文件会在项目根目录下自动生成。

### 5）可选：接入真实 EmQuant 数据

默认情况下，项目会走 `core/emquant_client.py` 中的 **mock 持仓数据**，所以即使没有安装 EmQuant SDK，也能正常启动。

如果你后续希望接入真实数据：

1. 安装并配置 EmQuant 官方 Python SDK
2. 根据你的 SDK 实际接口修改 `core/emquant_client.py`
3. 在 `_fetch_positions_from_sdk()` 中返回统一结构的持仓列表

如果 SDK 不可用，系统会自动回退到 mock 数据。

---

## 启动方式

### 开发模式启动

```bash
uvicorn main:app --reload
```

启动成功后，默认访问地址：

- 首页看板：`http://127.0.0.1:8000/dashboard`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/healthz`

根路径 `/` 会自动跳转到 `/dashboard`。

### 指定端口启动

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

如果你想换端口，例如 9000：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

此时访问地址变为：

- `http://127.0.0.1:9000/dashboard`

---

## 首次启动时会发生什么

应用启动时会执行以下初始化流程：

1. 创建数据库连接
2. 自动创建数据表
3. 初始化 SQLAlchemy Session
4. 初始化 EmQuant 客户端
5. 初始化 AIEngine
6. 检查数据库中是否已有持仓数据
7. 如果没有，则写入默认 mock 持仓
8. 启动 APScheduler 定时任务

也就是说，**首次运行不需要额外初始化命令，直接启动即可**。

---

## 主要功能

### 1）持仓看板

访问：

```text
GET /dashboard
```

用于展示一体化持仓看板页面。

### 2）获取当前持仓

```text
GET /api/skill/get_positions
```

返回：

- 持仓明细 `positions`
- 分组信息 `groups`
- 汇总信息 `totals`

### 3）更新策略信息

```text
POST /api/skill/update_strategy
```

请求示例：

```json
{
  "symbol": "600519.SH",
  "portfolio_tag": "核心组合",
  "strategy_description": "白马龙头，继续观察趋势强度",
  "expected_action": "若放量突破则继续持有"
}
```

说明：

- `symbol`：股票代码，必填
- `portfolio_tag`：组合标签，可选
- `strategy_description`：策略描述，可选
- `expected_action`：预期操作，可选

如果目标持仓不存在，会返回 `404 Position not found`。

---

## 定时任务说明

项目内置两个后台任务：

1. **持仓同步任务**
   - 执行频率：每 10 分钟一次
   - 作用：刷新当前持仓信息

2. **尾盘建议任务**
   - 执行时间：工作日 14:30（Asia/Shanghai）
   - 作用：调用 `AIEngine` 生成尾盘建议

如果你只是本地开发调试，这两个任务会在应用启动后自动注册并运行。

---

## 常见开发操作

### 删除本地数据库，重新初始化

如果你想重置数据，可以先停止服务，然后删除数据库文件：

```bash
rm -f alpha_local.db
```

Windows PowerShell：

```powershell
Remove-Item alpha_local.db
```

删除后重新执行启动命令，系统会自动重新建表并写入初始 mock 数据。

### 查看接口文档

启动后打开：

```text
http://127.0.0.1:8000/docs
```

可直接在线调试 API。

### 运行测试

如果仓库中的 `tests/` 已补充测试用例，可执行：

```bash
pytest
```

如果本地尚未安装 `pytest`，需要额外安装：

```bash
pip install pytest
```

---

## 常见问题

### 1）没有安装 EmQuant SDK，可以运行吗？

可以。项目默认会自动回退到 mock 数据。

### 2）为什么启动后目录里多了 `alpha_local.db`？

这是 SQLite 数据库文件，属于正常现象。

### 3）为什么访问 `/` 会跳转？

因为根路由被设计为自动重定向到 `/dashboard`。

### 4）前端需要单独 `npm install` / `npm run dev` 吗？

当前版本**不需要**。前端静态资源已经集成到服务端项目中，直接启动 FastAPI 即可。

---

## 后续可扩展方向

- 接入真实券商 / 行情数据源
- 增加用户体系与登录鉴权
- 支持多账户、多策略组合
- 增加更完整的 AI 投资建议链路
- 增加 pytest 测试与 CI 流程
- 增加 Docker 部署配置

---

## 快速开始

如果你只想最快跑起来：

```bash
git clone https://github.com/wangweijia/Alpha-Local.git
cd Alpha-Local
python -m venv .venv
source .venv/bin/activate  # Windows 请改用对应激活命令
pip install -r requirements.txt
uvicorn main:app --reload
```

然后打开：

```text
http://127.0.0.1:8000/dashboard
```
