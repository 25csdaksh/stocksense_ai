"""
AI Multi-Agent Intelligence & Real-Time SSE Streaming Routes.
"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.schemas.ai import AgentQueryRequest, AgentQueryResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Multi-Agent Intelligence"])


@router.post("/analyze", response_model=AgentQueryResponse)
@router.post("/query", response_model=AgentQueryResponse)
async def analyze_with_multi_agent(req: AgentQueryRequest):
    """Executes the complete multi-agent LangGraph workflow (Supervisor -> Data -> Quant -> RAG -> Synthesis)."""
    return await ai_service.execute_query(query=req.query, session_id=req.session_id or "default_session")


@router.get("/stream")
async def stream_agent_execution(
    query: str = Query(..., min_length=2, description="User financial question or scenario prompt"),
    session_id: str = Query(default="default_session", description="Session identifier for state tracking")
):
    """Streams real-time multi-agent reasoning thoughts, tool invocations, UI widgets, and tokens over Server-Sent Events (SSE)."""
    return StreamingResponse(
        ai_service.stream_query(query=query, session_id=session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
