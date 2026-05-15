# Alpha-Local

> 一个基于 **FastAPI + Jinja2 + Vue3（本地静态资源集成）** 的本地投资辅助系统示例。
> 适合作为 **本地原型、课程示例、个人作品集项目**，也适合作为后续接入真实行情、券商 SDK 与 AI 分析能力的基础工程。

## 项目简介

Alpha-Local 将页面渲染、技能 API、SQLite 存储与定时任务统一收敛在同一个 Python 服务中，目标是提供一个“**本地可运行、前后端一体化、具备投资辅助能力**”的最小完整系统。

它不是一个拆分复杂的多服务工程，而是一个强调以下特点的单体项目模板：

- 快速启动
- 本地可演示
- 便于二次开发
- 便于接入真实数据源
- 适合作品集展示

你可以把它理解成一个适合继续扩展的基础版本，后续可以逐步演进为：

- 个人投资辅助工作台
- 多账户策略管理平台
- 接入券商 / 行情 / AI 分析服务的本地系统
- 用于展示工程能力的作品集项目

---

## 项目亮点

- **单体架构，开箱即跑**：后端页面、API、数据库、定时任务都在同一个服务中。
- **本地数据库存储**：默认使用 SQLite，本地启动时会自动初始化数据库文件。
- **默认内置 Mock 持仓数据**：即使没有接入真实行情 / 券商 SDK，也可以直接看到页面效果。
- **支持后续接入 EmQuant SDK**：`core/emquant_client.py` 已预留真实持仓获取逻辑。
- **带有定时任务**：
  - 每 10 分钟自动同步一次持仓
  - 每个工作日 14:30 生成一次尾盘建议
- **自带前端页面**：启动后可直接访问 dashboard，无需额外单独启动前端工程。
- **适合作为二次开发基础**：目录结构清晰，适合继续扩展用户系统、策略系统、真实数据接入与部署能力。

---

## 技术栈

### 后端

- FastAPI
- SQLAlchemy
- Jinja2
- APScheduler
- Uvicorn

### 数据层

- SQLite（默认）

### 前端

- Vue3（以本地静态资源方式集成）
- HTML / CSS 模板页面

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
├── Dockerfile           # Docker 镜像构建文件（如已添加）
├── docker-compose.yml   # Docker 编排文件（如已添加）
└── README.md
```

如果你准备继续扩展项目，可以重点关注以下模块：

- `main.py`：应用生命周期、路由挂载、定时任务初始化
- `api/skills.py`：对外暴露的核心 API
- `models/database.py`：数据库初始化与 Session 管理
- `core/emquant_client.py`：真实持仓数据接入入口
- `core/ai_engine.py`：AI 建议生成逻辑入口

---

## 环境要求

建议使用以下环境：

- Python **3.10+**（推荐 3.11）
- pip 最新版本
- 操作系统：macOS / Linux / Windows 均可

可以先确认 Python 版本：

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

建议保持返回结构与当前 mock 数据一致，例如：

```json
[
  {
    "symbol": "600519.SH",
    "name": "贵州茅台",
    "quantity": 100,
    "average_cost": 1680.0,
    "last_price": 1715.5,
    "portfolio_tag": "长线",
    "strategy_description": "核心白马，逢回调观察加仓",
    "expected_action": "若放量突破则继续持有"
  }
]
```

如果 SDK 不可用，系统会自动回退到 mock 数据。

---

## 启动方式

### 本地开发模式启动

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

## Docker 部署说明

> 如果你还没有添加 `Dockerfile` 或 `docker-compose.yml`，可以先参考以下规范补充。

### 方式一：使用 Dockerfile 构建并运行

先在项目根目录准备一个基础 `Dockerfile`（���果仓库还没有的话）：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

然后执行：

```bash
docker build -t alpha-local .
docker run --rm -p 8000:8000 alpha-local
```

启动后访问：

```text
http://127.0.0.1:8000/dashboard
```

### 方式二：使用 docker-compose 启动

如果你希望用 `docker-compose` 管理服务，可以新建 `docker-compose.yml`：

```yaml
version: '3.9'
services:
  alpha-local:
    build: .
    container_name: alpha-local
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动命令：

```bash
docker compose up --build
```

后台启动：

```bash
docker compose up -d --build
```

停止服务：

```bash
docker compose down
```

### Docker 使用建议

如果后续要长期部署，建议进一步优化：

- 将数据库路径挂载到宿主机卷
- 使用 `.env` 管理环境变量
- 将 `--reload` 仅用于开发环境
- 为日志与数据目录单独挂载 volume

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

## 推荐体验流程

如果你是第一次运行项目，推荐按下面顺序体验：

1. 启动服务
2. 打开 `http://127.0.0.1:8000/dashboard`
3. 查看默认 mock 持仓是否展示正常
4. 打开 `http://127.0.0.1:8000/docs`
5. 调用 `GET /api/skill/get_positions` 查看接口返回
6. 调用 `POST /api/skill/update_strategy` 修改某只股票的策略信息
7. 刷新 dashboard，观察页面变化

这套流程适合快速确认：

- 服务是否启动正常
- 数据库是否正常初始化
- API 是否可用
- 页面与后端数据是否打通

---

## 核心功能

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

接口示例响应（示意）：

```json
{
  "positions": [
    {
      "symbol": "600519.SH",
      "name": "贵州茅台",
      "quantity": 100,
      "portfolio_tag": "长线"
    }
  ],
  "groups": {
    "长线": ["600519.SH"]
  },
  "totals": {
    "position_count": 1
  }
}
```

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

## curl / httpie 接口调用示例

### 获取当前持仓

#### curl

```bash
curl -X GET "http://127.0.0.1:8000/api/skill/get_positions"
```

#### httpie

```bash
http GET http://127.0.0.1:8000/api/skill/get_positions
```

### 更新策略信息

#### curl

```bash
curl -X POST "http://127.0.0.1:8000/api/skill/update_strategy" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "portfolio_tag": "核心组合",
    "strategy_description": "白马龙头，继续观察趋势强度",
    "expected_action": "若放量突破则继续持有"
  }'
```

#### httpie

```bash
http POST http://127.0.0.1:8000/api/skill/update_strategy \
  symbol=600519.SH \
  portfolio_tag="核心组合" \
  strategy_description="白马龙头，继续观察趋势强度" \
  expected_action="若放量突破则继续持有"
```

### 健康检查

#### curl

```bash
curl -X GET "http://127.0.0.1:8000/healthz"
```

#### httpie

```bash
http GET http://127.0.0.1:8000/healthz
```

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

### 格式化与规范建议

当前仓库尚未看到统一的格式化与检查工具配置。如果你后续准备长期维护，建议补充：

- `black`
- `ruff`
- `pytest`
- `pre-commit`

例如：

```bash
pip install black ruff pytest pre-commit
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

### 5）如果想切换成真实数据库怎么办？

目前代码中默认使用 SQLite。本项目结构已经具备切换到其他数据库的基础能力，如果后续要升级，可考虑：

- PostgreSQL
- MySQL

前提是补充数据库连接配置，并将数据库 URL 从代码中抽离到环境变量。

---

## 作品集展示建议

如果你想把它作为作品集项目，建议继续补充以下内容：

1. **项目截图**：首页、持仓表格、策略编辑页面
2. **部署说明**：Docker、本地服务器、云主机部署
3. **设计说明**：为什么采用 FastAPI + Jinja2 + SQLite 的组合
4. **演进规划**：从本地原型到可部署系统的升级路径
5. **真实数据接入说明**：如何从 mock 数据切换到真实券商 / 行情数据

这样 README 会更适合：

- 求职作品集展示
- GitHub 公开仓库展示
- 面试时介绍项目
- 向他人说明你的工程设计思路

---

## Roadmap

### 当前已完成

- [x] 本地持仓看板
- [x] 技能 API
- [x] SQLite 本地存储
- [x] 定时同步任务
- [x] Mock 数据启动能力

### 后续计划

- [ ] 接入真实 EmQuant / 券商数据
- [ ] 增加用户登录与鉴权
- [ ] 增加策略历史记录
- [ ] 增加 AI 建议落库与展示
- [ ] 提供 Docker 部署方式
- [ ] 增加测试覆盖率
- [ ] 增加 CI / CD 流程

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
