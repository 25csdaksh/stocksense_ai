"""
AI Query Execution & Database Logging Integration Tests.
Verifies that multi-agent execution results, citations, and public tool metadata are persisted to PostgreSQL.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from app.db.models.ai import ChatSession, AIQuery
from app.db.repositories.ai_query_repository import AIQueryRepository


@pytest.mark.asyncio
async def test_ai_query_repository_logging(db_session: AsyncSession):
    repo = AIQueryRepository(db_session)

    # 1. Create / Retrieve Chat Session
    chat_session = await repo.get_or_create_session(
        session_id=None,
        title="NVIDIA Valuation Analysis"
    )
    assert chat_session.id is not None
    assert chat_session.title == "NVIDIA Valuation Analysis"

    # 2. Log AI Query
    logged = await repo.log_query(
        session_id=chat_session.id,
        query_text="What is NVIDIA's revenue concentration risk according to 10-K?",
        intent="FUNDAMENTAL_ANALYSIS",
        ticker_focus="NVDA",
        thought_steps=[
            {"step": 1, "agent": "orchestrator", "message": "Routing to SEC RAG specialist"},
            {"step": 2, "agent": "rag_specialist", "message": "Retrieved Item 1A Risk Factors"}
        ],
        tool_calls=[
            {"tool": "query_sec_10k", "arguments": {"ticker": "NVDA", "section": "Item 1A"}}
        ],
        answer="NVIDIA relies on TSMC for semiconductor wafer fabrication.",
        citations=[
            {"title": "NVDA 2024 Form 10-K", "section": "Item 1A", "page_number": 34, "ticker": "NVDA"}
        ],
        ui_widgets=[
            {"type": "metric_card", "title": "Customer Concentration", "value": "Customer A represents 13% of revenue"}
        ],
        guardrail_passed=True
    )
    await db_session.commit()

    assert logged.id is not None
    assert logged.session_id == chat_session.id
    assert logged.query_text == "What is NVIDIA's revenue concentration risk according to 10-K?"
    assert logged.ticker_focus == "NVDA"
    assert len(logged.citations) == 1
    assert logged.citations[0]["ticker"] == "NVDA"

    # 3. Verify record in database
    stmt = select(AIQuery).where(AIQuery.session_id == chat_session.id)
    res = await db_session.execute(stmt)
    records = res.scalars().all()
    assert len(records) == 1
    assert records[0].intent == "FUNDAMENTAL_ANALYSIS"


def test_ai_analyze_endpoint_e2e_db_persistence(test_client: TestClient):
    req_body = {
        "query": "Analyze AAPL technical momentum and key support levels",
        "session_id": "test_e2e_session_01"
    }
    resp = test_client.post("/api/v1/ai/analyze", json=req_body)
    assert resp.status_code == 200
    data = resp.json()

    assert "answer" in data
    assert "thought_steps" in data
    assert "citations" in data
    assert len(data["thought_steps"]) > 0
