"""
AI Multi-Agent Query, Streaming Event & Thought Schemas.
Phase 6.9: Extended schemas for full research plans, execution summaries, provenance, and structured reports.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    session_id: Optional[str] = "default_session"
    depth: Optional[str] = "STANDARD"
    symbols: Optional[List[str]] = None


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
    thought_steps: List[AgentThoughtStep] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    answer: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    ui_widgets: List[UIWidgetPayload] = Field(default_factory=list)
    guardrail_passed: bool = True
    # Phase 6.9 Extended Research Fields
    research_plan: Optional[Dict[str, Any]] = None
    execution_summary: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, str]] = None
    limitations: Optional[List[str]] = None
    cached: Optional[bool] = False
