from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from models.entities import Position


def serialize_position(position: Position) -> dict[str, object]:
    market_value = round(position.quantity * position.last_price, 2)
    unrealized_pnl = round(position.quantity * (position.last_price - position.average_cost), 2)
    return_pct = round(((position.last_price - position.average_cost) / position.average_cost) * 100, 2) if position.average_cost else 0.0
    return {
        "symbol": position.symbol,
        "name": position.name,
        "quantity": position.quantity,
        "average_cost": position.average_cost,
        "last_price": position.last_price,
        "market_value": market_value,
        "unrealized_pnl": unrealized_pnl,
        "return_pct": return_pct,
        "portfolio_tag": position.portfolio_tag,
        "strategy_description": position.strategy_description,
        "expected_action": position.expected_action,
        "updated_at": position.updated_at.isoformat() if position.updated_at else None,
    }


def summarize_positions(positions: Iterable[Position]) -> dict[str, object]:
    serialized = [serialize_position(position) for position in positions]
    totals = {
        "market_value": round(sum(item["market_value"] for item in serialized), 2),
        "unrealized_pnl": round(sum(item["unrealized_pnl"] for item in serialized), 2),
    }
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in serialized:
        grouped[str(item["portfolio_tag"] or "未分组")].append(item)
    return {"totals": totals, "groups": grouped, "positions": serialized}
