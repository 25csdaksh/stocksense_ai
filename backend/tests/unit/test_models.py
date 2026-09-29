"""
Unit Tests: SQLAlchemy 2.0 ORM Models Instantiation & Relationships.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    User, Sector, Company, Stock, StockOHLCV, MarketIndex,
    Fundamental, FinancialStatement, News, Anomaly, ScenarioReport,
    Portfolio, Position, Transaction, Watchlist, ChatSession, AIQuery,
    ResearchDocument, ResearchChunk
)
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_orm_models_instantiation(db_session: AsyncSession):
    user = User(
        username="unit_trader",
        email="unit@marketmind.ai",
        hashed_password=hash_password("test_pass")
    )
    db_session.add(user)
    await db_session.flush()

    sec = Sector(name="Information Technology", code="TECH")
    db_session.add(sec)
    await db_session.flush()

    comp = Company(name="Apple Inc.", ticker="AAPL", sector_id=sec.id)
    db_session.add(comp)
    await db_session.flush()

    stk = Stock(company_id=comp.id, ticker="AAPL", beta=1.12)
    db_session.add(stk)
    await db_session.flush()

    port = Portfolio(user_id=user.id, name="Test Port")
    db_session.add(port)
    await db_session.flush()

    pos = Position(portfolio_id=port.id, ticker="AAPL", shares=10.0, avg_cost=150.0)
    db_session.add(pos)

    tx = Transaction(portfolio_id=port.id, ticker="AAPL", shares=10.0, price=150.0, transaction_type="BUY")
    db_session.add(tx)

    wl = Watchlist(user_id=user.id, ticker="NVDA", target_price=500.0)
    db_session.add(wl)

    chat = ChatSession(user_id=user.id, title="Test Chat")
    db_session.add(chat)
    await db_session.flush()

    query = AIQuery(
        session_id=chat.id,
        user_id=user.id,
        query_text="What is AAPL beta?",
        intent="STOCK_QUERY",
        thought_steps=[],
        tool_calls=[],
        answer="1.12",
        citations=[],
        ui_widgets=[]
    )
    db_session.add(query)

    await db_session.commit()

    assert user.id is not None
    assert comp.id is not None
    assert pos.portfolio_id == port.id
    assert query.session_id == chat.id
