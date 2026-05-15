# Alpha-Local

一个基于 **FastAPI + Jinja2 + Vue3(本地静态资源集成)** 的单体化本地投资辅助系统示例，直接把页面渲染、技能 API、SQLite 存储与定时任务收敛在同一个 Python 服务进程中。

## 运行方式

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

启动后可访问：

- `http://127.0.0.1:8000/dashboard`：一体化持仓看板
- `http://127.0.0.1:8000/docs`：自动生成的 Skill API OpenAPI 文档

## 当前实现范围

- `GET /api/skill/get_positions`：获取当前自定义组合持仓状态
- `POST /api/skill/update_strategy`：更新股票的分组、持仓逻辑和期望动作
- APScheduler 内置 10 分钟持仓同步任务与工作日 14:30 尾盘 AI 建议任务
- 缺省情况下使用本地 mock 持仓数据启动；如后续安装东财官方 Python SDK，可在 `core/emquant_client.py` 中替换真实接入逻辑
- 为了兼容受限网络环境，Vue 运行时已作为本地静态资源随服务端一并提供
