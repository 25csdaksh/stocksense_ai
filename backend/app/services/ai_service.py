"""
AI Multi-Agent Service for Market Intelligence, Quant Scenario Orchestration & Reasoning.
Phase 6.9: Integrates MultiAgentResearchEngine as the primary research intelligence orchestrator.
"""
from typing import Dict, Any, AsyncGenerator, Optional
from app.ai.engine import multi_agent_engine
from app.agents.graph import agent_graph_runner
from app.ai.models import ResearchDepth


class AIService:

    def __init__(self):
        self.research_engine = multi_agent_engine
        self.legacy_runner = agent_graph_runner

    async def execute_query(
        self,
        query: str,
        session_id: str = "default_session",
        depth: Optional[str] = "STANDARD",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes multi-agent research analysis."""
        try:
            depth_enum = ResearchDepth(str(depth).upper()) if depth else ResearchDepth.STANDARD
        except ValueError:
            depth_enum = ResearchDepth.STANDARD

        try:
            return await self.research_engine.execute_research(
                query=query,
                depth=depth_enum,
                session_id=session_id,
                user_id=user_id
            )
        except Exception:
            # Resilient fallback to legacy graph runner
            return await self.legacy_runner.execute(query=query, session_id=session_id)

    async def stream_query(
        self,
        query: str,
        session_id: str = "default_session",
        depth: Optional[str] = "STANDARD",
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streams real-time research lifecycle events over SSE."""
        try:
            depth_enum = ResearchDepth(str(depth).upper()) if depth else ResearchDepth.STANDARD
        except ValueError:
            depth_enum = ResearchDepth.STANDARD

        async for event in self.research_engine.stream_research(
            query=query,
            depth=depth_enum,
            session_id=session_id,
            user_id=user_id
        ):
            yield event


ai_service = AIService()
