from __future__ import annotations

from core.portfolio_calc import summarize_positions
from models.entities import Position


class AIEngine:
    def build_prompt(self, positions: list[Position]) -> str:
        summary = summarize_positions(positions)
        return (
            "请基于以下持仓与盘面摘要，生成 14:30 尾盘操作建议：\n"
            f"总市值：{summary['totals']['market_value']}\n"
            f"总浮盈亏：{summary['totals']['unrealized_pnl']}\n"
            f"持仓数量：{len(summary['positions'])}"
        )

    def generate_pre_close_advice(self, positions: list[Position]) -> str:
        if not positions:
            return "暂无持仓数据，跳过 14:30 尾盘建议。"
        prompt = self.build_prompt(positions)
        return f"### Pre-Close Oracle\n\n{prompt}\n\n建议：优先处理策略描述中明确标记减仓条件的仓位。"
