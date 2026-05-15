from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.portfolio_calc import summarize_positions
from models.database import get_session
from models.entities import Position

router = APIRouter(prefix="/api/skill", tags=["skills"])


class StrategyUpdateRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    portfolio_tag: str | None = Field(default=None, description="虚拟组合标签")
    strategy_description: str | None = Field(default=None, description="持仓逻辑描述")
    expected_action: str | None = Field(default=None, description="期望的操作计划")


@router.get("/get_positions")
def get_positions(session: Session = Depends(get_session)) -> dict[str, object]:
    positions = session.query(Position).order_by(Position.symbol.asc()).all()
    summary = summarize_positions(positions)
    return {
        "positions": summary["positions"],
        "groups": summary["groups"],
        "totals": summary["totals"],
    }


@router.post("/update_strategy")
def update_strategy(payload: StrategyUpdateRequest, session: Session = Depends(get_session)) -> dict[str, object]:
    position = session.query(Position).filter(Position.symbol == payload.symbol).one_or_none()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    if payload.portfolio_tag is not None:
        cleaned_portfolio_tag = payload.portfolio_tag.strip()
        position.portfolio_tag = cleaned_portfolio_tag or "默认组合"
    if payload.strategy_description is not None:
        position.strategy_description = payload.strategy_description.strip()
    if payload.expected_action is not None:
        position.expected_action = payload.expected_action.strip()

    session.add(position)
    session.commit()
    session.refresh(position)
    return {"message": "Strategy updated", "position": summarize_positions([position])["positions"][0]}
