"""
AI Multi-Agent Conversation Session & Query History ORM Models.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Column, String, Text, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(200), default="Market Intelligence Session", nullable=False)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    queries = relationship("AIQuery", back_populates="session", cascade="all, delete-orphan")


class AIQuery(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_queries"

    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    intent = Column(String(50), default="MARKET_INTELLIGENCE", nullable=False)
    ticker_focus = Column(String(10), nullable=True, index=True)
    thought_steps = Column(JSON, nullable=False)
    tool_calls = Column(JSON, nullable=False)
    answer = Column(Text, nullable=False)
    citations = Column(JSON, nullable=False)
    ui_widgets = Column(JSON, nullable=False)
    guardrail_passed = Column(Boolean, default=True, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="queries")
    user = relationship("User", back_populates="ai_queries")
