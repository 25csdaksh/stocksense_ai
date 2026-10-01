"""
AI Multi-Agent Intelligence & Real-Time SSE Streaming Routes with Database Logging.
Phase 6.9: Unified AI research endpoints supporting multi-specialist planning, evidence synthesis, and streaming.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ai import AgentQueryRequest, AgentQueryResponse
from app.services.ai_service import ai_service
from app.db.session import get_db_session
from app.db.repositories.ai_query_repository import AIQueryRepository
from app.api.dependencies import get_optional_user

router = APIRouter(prefix="/ai", tags=["AI Multi-Agent Intelligence"])


@router.post("/analyze", response_model=AgentQueryResponse)
@router.post("/query", response_model=AgentQueryResponse)
async def analyze_with_multi_agent(
    req: AgentQueryRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Executes the complete multi-agent research workflow and logs query execution history to database."""
    session_id = req.session_id or "default_session"
    user_id = current_user["id"] if current_user else None
    result = await ai_service.execute_query(
        query=req.query,
        session_id=session_id,
        depth=req.depth,
        user_id=user_id
    )

    # Persist query execution record to DB
    try:
        ai_repo = AIQueryRepository(db)
        # Store only sanitized public thought steps and execution metadata
        clean_steps = [
            {"step": st.get("step", idx + 1), "agent": st.get("agent", "agent"), "message": st.get("message", "")}
            for idx, st in enumerate(result.get("thought_steps", []))
        ]
        await ai_repo.log_query(
            session_id=session_id,
            user_id=user_id,
            query_text=req.query,
            intent=result.get("intent", "MARKET_INTELLIGENCE"),
            ticker_focus=result.get("ticker_focus"),
            thought_steps=clean_steps,
            tool_calls=result.get("tool_calls", []),
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
            ui_widgets=result.get("ui_widgets", []),
            guardrail_passed=result.get("guardrail_passed", True)
        )
    except Exception:
        pass

    return result


@router.get("/stream")
async def stream_agent_execution(
    query: str = Query(..., min_length=2, description="User financial question or scenario prompt"),
    session_id: str = Query(default="default_session", description="Session identifier for state tracking"),
    depth: Optional[str] = Query(default="STANDARD", description="Research depth: QUICK, STANDARD, DEEP")
):
    """Streams real-time multi-agent research thoughts, specialist tasks, and report synthesis over SSE."""
    return StreamingResponse(
        ai_service.stream_query(query=query, session_id=session_id, depth=depth),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/query/stream")
async def post_stream_agent_execution(
    req: AgentQueryRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """POST endpoint for streaming research lifecycle events over Server-Sent Events (SSE)."""
    user_id = current_user["id"] if current_user else None
    return StreamingResponse(
        ai_service.stream_query(
            query=req.query,
            session_id=req.session_id or "default_session",
            depth=req.depth,
            user_id=user_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
