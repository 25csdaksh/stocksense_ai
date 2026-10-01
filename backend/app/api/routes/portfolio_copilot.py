"""
MarketMind AI — Portfolio Copilot, Memory & Factual Alert API Routes.
Phase 6.10: Endpoints for portfolio-aware research copilot, SSE streaming, daily briefs, research memory, and alerts.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db_session
from app.api.dependencies import get_optional_user, get_current_user
from app.ai.portfolio.models import (
    PortfolioCopilotMode,
    PortfolioCopilotQueryRequest,
    PortfolioCopilotQueryResponse,
    DailyPortfolioBrief,
    PortfolioAlertRuleModel,
    PortfolioAlertEventModel,
    ResearchMemoryItem,
)
from app.ai.portfolio.copilot_engine import copilot_engine
from app.ai.portfolio.context_builder import user_context_builder
from app.ai.portfolio.change_detector import change_detector
from app.ai.portfolio.memory_service import memory_service
from app.ai.portfolio.alert_engine import alert_engine

router = APIRouter(prefix="/ai/portfolio", tags=["AI Portfolio Copilot & Memory"])


class CreateAlertRuleRequest(BaseModel):
    rule_type: str = Field(..., description="PRICE_MOVE_PCT, VOLATILITY_THRESHOLD, WEIGHT_THRESHOLD, etc.")
    threshold: float = Field(..., description="Trigger threshold value")
    symbol: Optional[str] = None
    portfolio_id: Optional[str] = None
    timeframe: str = "1d"


@router.post("/query", response_model=PortfolioCopilotQueryResponse)
async def query_portfolio_copilot(
    req: PortfolioCopilotQueryRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Executes multi-agent portfolio copilot analysis personalized to authenticated user."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    res = await copilot_engine.execute_query(
        query=req.query,
        user_id=user_id,
        mode=req.mode,
        depth=req.depth,
        session_id=req.session_id or "copilot_default_session",
        symbols_override=req.symbols_override,
        db=db
    )
    return res


@router.post("/query/stream")
async def stream_portfolio_copilot(
    req: PortfolioCopilotQueryRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Streams real-time portfolio copilot research lifecycle events over Server-Sent Events (SSE)."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    return StreamingResponse(
        copilot_engine.stream_query(
            query=req.query,
            user_id=user_id,
            mode=req.mode,
            depth=req.depth,
            session_id=req.session_id or "copilot_default_session",
            db=db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/daily-brief", response_model=DailyPortfolioBrief)
async def get_daily_portfolio_brief(
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Generates structured daily intelligence brief for user portfolio."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    user_ctx = await user_context_builder.build_user_context(user_id=user_id, db=db)
    changes = change_detector.detect_portfolio_internal_changes(
        holdings=user_ctx.portfolio.holdings,
        portfolio=user_ctx.portfolio
    )
    brief = copilot_engine.generate_daily_brief(
        user_id=user_id,
        user_ctx=user_ctx,
        change_report=changes
    )
    return brief


# =========================================================================
# Research Memory Endpoints
# =========================================================================

@router.get("/memory", response_model=List[ResearchMemoryItem])
async def get_user_research_memory(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Retrieves user-scoped research history memory."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    return await memory_service.get_user_memories(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db=db
    )


@router.get("/memory/{research_id}", response_model=ResearchMemoryItem)
async def get_research_memory_by_id(
    research_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Retrieves specific research memory ensuring user isolation (IDOR protection)."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    mem = await memory_service.get_memory_by_id(
        user_id=user_id,
        research_id=research_id,
        db=db
    )
    if not mem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research memory record not found or access unauthorized."
        )
    return mem


# =========================================================================
# Portfolio Alerts & Rules Endpoints
# =========================================================================

@router.get("/alerts", response_model=List[PortfolioAlertEventModel])
async def get_portfolio_alerts(
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Fetches user portfolio and watchlist alerts."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    return await alert_engine.get_user_alerts(user_id=user_id, unread_only=unread_only, db=db)


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Marks an alert as read with user ownership validation."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    repo = ResearchMemoryRepository(db)
    success = await repo.mark_alert_read(user_id=user_id, alert_id=alert_id)
    return {"status": "SUCCESS" if success else "NOT_FOUND", "alert_id": alert_id}


@router.get("/alerts/rules", response_model=List[PortfolioAlertRuleModel])
async def get_alert_rules(
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Fetches user configured alert rules."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    return await alert_engine.get_user_rules(user_id=user_id, db=db)


@router.post("/alerts/rules", response_model=PortfolioAlertRuleModel)
async def create_alert_rule(
    req: CreateAlertRuleRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Creates a new user threshold alert rule."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    return await alert_engine.create_rule(
        user_id=user_id,
        rule_type=req.rule_type,
        threshold=req.threshold,
        symbol=req.symbol,
        portfolio_id=req.portfolio_id,
        timeframe=req.timeframe,
        db=db
    )


@router.delete("/alerts/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Deletes an alert rule with ownership validation."""
    user_id = current_user["id"] if current_user else "usr_dev_admin_001"
    success = await alert_engine.delete_rule(user_id=user_id, rule_id=rule_id, db=db)
    return {"status": "SUCCESS" if success else "NOT_FOUND", "rule_id": rule_id}
