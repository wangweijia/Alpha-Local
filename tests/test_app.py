from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import create_app
from models.entities import Position


class AlphaLocalAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        self.connect_patcher = patch("main.EmQuantClient.connect", return_value=True)
        self.fetch_patcher = patch("main.EmQuantClient.fetch_positions", return_value=[])
        self.connect_patcher.start()
        self.fetch_patcher.start()
        self.app = create_app(database_url=f"sqlite:///{database_path}", start_scheduler=False)
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()
        self._seed_positions()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.fetch_patcher.stop()
        self.connect_patcher.stop()
        self.temp_dir.cleanup()

    def _seed_positions(self) -> None:
        with self.app.state.SessionLocal() as session:
            session.add_all(
                [
                    Position(
                        symbol="600519.SH",
                        name="贵州茅台",
                        quantity=100,
                        average_cost=1680.0,
                        last_price=1715.5,
                        portfolio_tag="长线",
                        strategy_description="核心白马，逢回调观察加仓",
                        expected_action="若放量突破则继续持有",
                    ),
                    Position(
                        symbol="300750.SZ",
                        name="宁德时代",
                        quantity=200,
                        average_cost=225.0,
                        last_price=219.8,
                        portfolio_tag="波段",
                        strategy_description="跟踪新能源景气度",
                        expected_action="尾盘若弱势延续则减仓",
                    ),
                ]
            )
            session.commit()

    def test_dashboard_renders_monolith_ui(self) -> None:
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alpha-Local 持仓看板", response.text)
        self.assertIn("/static/vendor/vue.global.prod.js", response.text)
        self.assertIn("/api/skill/get_positions", response.text)

    def test_get_positions_returns_seeded_data(self) -> None:
        response = self.client.get("/api/skill/get_positions")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload["positions"]), 2)
        self.assertIn("totals", payload)

    def test_update_strategy_persists_changes(self) -> None:
        update_response = self.client.post(
            "/api/skill/update_strategy",
            json={
                "symbol": "600519.SH",
                "portfolio_tag": "尾盘观察",
                "strategy_description": "关注量能确认",
                "expected_action": "若 14:30 后放量则持有",
            },
        )
        self.assertEqual(update_response.status_code, 200)

        get_response = self.client.get("/api/skill/get_positions")
        self.assertEqual(get_response.status_code, 200)
        position = next(item for item in get_response.json()["positions"] if item["symbol"] == "600519.SH")
        self.assertEqual(position["portfolio_tag"], "尾盘观察")
        self.assertEqual(position["strategy_description"], "关注量能确认")
        self.assertEqual(position["expected_action"], "若 14:30 后放量则持有")

    def test_update_strategy_blank_tag_resets_to_default_group(self) -> None:
        update_response = self.client.post(
            "/api/skill/update_strategy",
            json={
                "symbol": "600519.SH",
                "portfolio_tag": "   ",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["position"]["portfolio_tag"], "默认组合")


if __name__ == "__main__":
    unittest.main()
