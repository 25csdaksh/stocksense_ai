"""
AI Multi-Agent Streaming & Reasoning Endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas.agent_schema import AgentQueryRequest, AgentQueryResponse
from services.agent_service import agent_service

router = APIRouter(prefix="/agent", tags=["AI Multi-Agent"])


@router.post("/query", response_model=AgentQueryResponse)
async def query_ai_agent(req: AgentQueryRequest):
    """Executes multi-step agent reasoning workflow synchronously and returns structured answer and citations."""
    return await agent_service.run_query(query=req.query, session_id=req.session_id or "default")


@router.get("/stream")
async def stream_ai_agent(query: str, session_id: str = "default"):
    """Server-Sent Events (SSE) endpoint streaming real-time thoughts, tool calls, and UI chart widgets."""
    return StreamingResponse(
        agent_service.stream_agent_execution(query=query, session_id=session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
