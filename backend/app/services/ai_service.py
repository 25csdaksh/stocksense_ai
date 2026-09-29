"""
AI Multi-Agent Service for Market Intelligence, Quant Scenario Orchestration & Reasoning.
"""
from typing import Dict, Any, AsyncGenerator
from app.agents.graph import agent_graph_runner


class AIService:

    def __init__(self):
        self.runner = agent_graph_runner

    async def execute_query(self, query: str, session_id: str = "default_session") -> Dict[str, Any]:
        return await self.runner.execute(query=query, session_id=session_id)

    async def stream_query(self, query: str, session_id: str = "default_session") -> AsyncGenerator[str, None]:
        async for event in self.runner.stream(query=query, session_id=session_id):
            yield event


ai_service = AIService()
