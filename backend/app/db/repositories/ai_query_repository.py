"""
AI Multi-Agent Chat Sessions & Query Execution History Repository.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.repositories.base import BaseRepository
from app.db.models.ai import ChatSession, AIQuery


class AIQueryRepository(BaseRepository[AIQuery]):

    def __init__(self, session: AsyncSession):
        super().__init__(AIQuery, session)

    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        title: str = "Market Intelligence Session",
        user_id: Optional[str] = None
    ) -> ChatSession:
        if session_id:
            stmt = select(ChatSession).where(ChatSession.id == session_id)
            res = await self.session.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                return existing

        chat_session = ChatSession(
            id=session_id if session_id and len(session_id) == 36 else None,
            title=title,
            user_id=user_id
        )
        self.session.add(chat_session)
        await self.session.flush()
        return chat_session

    async def log_query(
        self,
        session_id: str,
        query_text: str,
        intent: str,
        ticker_focus: Optional[str],
        thought_steps: List[Dict[str, Any]],
        tool_calls: List[Dict[str, Any]],
        answer: str,
        citations: List[Dict[str, Any]],
        ui_widgets: List[Dict[str, Any]],
        guardrail_passed: bool = True,
        user_id: Optional[str] = None
    ) -> AIQuery:
        # Ensure session exists
        session = await self.get_or_create_session(session_id=session_id, user_id=user_id)
        
        query_log = AIQuery(
            session_id=session.id,
            user_id=user_id,
            query_text=query_text,
            intent=intent,
            ticker_focus=ticker_focus,
            thought_steps=thought_steps,
            tool_calls=tool_calls,
            answer=answer,
            citations=citations,
            ui_widgets=ui_widgets,
            guardrail_passed=guardrail_passed
        )
        self.session.add(query_log)
        await self.session.flush()
        return query_log
