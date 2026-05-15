from __future__ import annotations

from typing import Any


class EmQuantClient:
    def __init__(self) -> None:
        self._sdk = None
        self.connected = False
        try:
            from EmQuantAPI import c  # type: ignore

            self._sdk = c
        except ImportError:
            self._sdk = None

    @property
    def sdk_available(self) -> bool:
        return self._sdk is not None

    def connect(self) -> bool:
        self.connected = True
        return self.connected

    def fetch_positions(self) -> list[dict[str, Any]]:
        if self.sdk_available and self._sdk is not None:
            return []
        return [
            {
                "symbol": "600519.SH",
                "name": "贵州茅台",
                "quantity": 100,
                "average_cost": 1680.0,
                "last_price": 1715.5,
                "portfolio_tag": "长线",
                "strategy_description": "核心白马，逢回调观察加仓",
                "expected_action": "若放量突破则继续持有",
            },
            {
                "symbol": "300750.SZ",
                "name": "宁德时代",
                "quantity": 200,
                "average_cost": 225.0,
                "last_price": 219.8,
                "portfolio_tag": "波段",
                "strategy_description": "跟踪新能源景气度",
                "expected_action": "尾盘若弱势延续则减仓",
            },
        ]
