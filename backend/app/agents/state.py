"""
LangGraph Multi-Agent State Definition.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator


class AgentState(TypedDict):
    query: str
    session_id: str
    ticker_focus: Optional[str]
    intent: str
    thought_steps: Annotated[List[Dict[str, Any]], operator.add]
    tool_calls: Annotated[List[Dict[str, Any]], operator.add]
    data_context: Annotated[Dict[str, Any], operator.ior]
    retrieved_citations: Annotated[List[Dict[str, Any]], operator.add]
    ui_widgets: Annotated[List[Dict[str, Any]], operator.add]
    final_answer: Optional[str]
    guardrail_passed: bool
