"""
AI Multi-Agent Schemas for Query Execution & SSE Streaming.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="User financial question or scenario prompt")
    session_id: Optional[str] = Field(default="default_session")
    ticker_focus: Optional[str] = None


class AgentThoughtStep(BaseModel):
    step_number: int
    agent_name: str  # 'Supervisor', 'DataFetcher', 'QuantEngine', 'RAGSearch', 'Synthesis'
    action: str
    status: str      # 'in_progress', 'completed', 'failed'
    details: Optional[Dict[str, Any]] = None


class UIWidgetPayload(BaseModel):
    widget_type: str  # 'FAN_CHART', 'RADAR_DNA', 'ANOMALY_CARD', 'RATIO_GRID', 'CORRELATION_HEATMAP'
    title: str
    data: Any


class AgentQueryResponse(BaseModel):
    session_id: str
    query: str
    intent: str
    thought_steps: List[AgentThoughtStep]
    answer: str
    retrieved_citations: List[Dict[str, Any]]
    ui_widgets: List[UIWidgetPayload]
    data_source_badge: str
    educational_disclaimer: str


class AgentStreamChunk(BaseModel):
    event: str       # 'thought', 'tool_call', 'tool_result', 'token', 'widget', 'final', 'error'
    data: Dict[str, Any]
