"""
AI Multi-Agent Query, Streaming Event & Thought Schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    session_id: Optional[str] = "default_session"


class AgentThoughtStep(BaseModel):
    step: int
    agent: str
    message: str


class UIWidgetPayload(BaseModel):
    widget_type: str
    title: str
    data: Any


class AgentQueryResponse(BaseModel):
    session_id: str
    query: str
    intent: str
    ticker_focus: Optional[str] = None
    thought_steps: List[AgentThoughtStep]
    tool_calls: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    ui_widgets: List[UIWidgetPayload]
    guardrail_passed: bool
