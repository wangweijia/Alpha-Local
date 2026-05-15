from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.skills import router as skills_router
from core.ai_engine import AIEngine
from core.emquant_client import EmQuantClient
from models.database import configure_database, get_session_factory, init_database
from models.entities import Position

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'alpha_local.db'}"


def seed_positions(app: FastAPI) -> None:
    with app.state.SessionLocal() as session:
        if session.query(Position).count() > 0:
            return
        for payload in app.state.emquant_client.fetch_positions():
            session.add(Position(**payload))
        session.commit()


def sync_positions(app: FastAPI) -> None:
    payloads = app.state.emquant_client.fetch_positions()
    with app.state.SessionLocal() as session:
        for payload in payloads:
            position = session.query(Position).filter(Position.symbol == payload["symbol"]).one_or_none()
            if position is None:
                session.add(Position(**payload))
                continue
            position.name = payload["name"]
            position.quantity = payload["quantity"]
            position.average_cost = payload["average_cost"]
            position.last_price = payload["last_price"]
            position.portfolio_tag = payload["portfolio_tag"]
            position.strategy_description = payload["strategy_description"]
            position.expected_action = payload["expected_action"]
        session.commit()


def run_pre_close_oracle(app: FastAPI) -> str:
    with app.state.SessionLocal() as session:
        positions = session.query(Position).order_by(Position.symbol.asc()).all()
        advice = app.state.ai_engine.generate_pre_close_advice(positions)
    app.state.last_pre_close_advice = advice
    return advice


def build_scheduler(app: FastAPI) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(sync_positions, "interval", minutes=10, args=[app], id="position-sync", replace_existing=True)
    scheduler.add_job(
        run_pre_close_oracle,
        CronTrigger(day_of_week="mon-fri", hour=14, minute=30, timezone="Asia/Shanghai"),
        args=[app],
        id="pre-close-oracle",
        replace_existing=True,
    )
    return scheduler


def create_app(database_url: str | None = None, start_scheduler: bool = True) -> FastAPI:
    resolved_database_url = database_url or DEFAULT_DATABASE_URL
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = configure_database(resolved_database_url)
        init_database()
        app.state.engine = engine
        app.state.SessionLocal = get_session_factory()
        app.state.templates = templates
        app.state.emquant_client = EmQuantClient()
        app.state.emquant_client.connect()
        app.state.ai_engine = AIEngine()
        app.state.last_pre_close_advice = ""
        seed_positions(app)
        app.state.scheduler = build_scheduler(app) if start_scheduler else None
        if app.state.scheduler is not None:
            app.state.scheduler.start()
        try:
            yield
        finally:
            if app.state.scheduler is not None:
                app.state.scheduler.shutdown(wait=False)
            engine.dispose()

    app = FastAPI(
        title="Alpha-Local",
        description="单体集成版个人投资与 AI 辅助决策系统",
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    app.include_router(skills_router)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/dashboard")

    @app.get("/dashboard")
    def dashboard(request: Request):
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "page_title": "Alpha-Local Dashboard",
                "api_base": "/api/skill",
            },
        )

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
