"""
AI Multi-Agent Pipeline & Query Validation Tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.ai import AgentQueryRequest
from app.services.ai_service import ai_service

client = TestClient(app)


def test_ai_query_validation_error():
    # Empty query should fail validation
    response = client.post("/api/v1/ai/analyze", json={"query": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_service_multi_agent_execution():
    res = await ai_service.execute_query(
        query="Analyze Apple AAPL market valuation and regulatory risks",
        session_id="test_sess_001"
    )

    assert "session_id" in res
    assert res["session_id"] == "test_sess_001"
    assert "intent" in res
    assert "thought_steps" in res
    assert len(res["thought_steps"]) > 0
    assert "answer" in res
    assert len(res["answer"]) > 0
    assert res["guardrail_passed"] is True


@pytest.mark.asyncio
async def test_ai_service_streaming():
    events = []
    async for event in ai_service.stream_query(query="NVDA scenario", session_id="test_stream_001"):
        events.append(event)

    assert len(events) > 0
    # Must contain SSE formatted strings
    assert any("event: thought" in ev for ev in events)
    assert any("event: final" in ev for ev in events)
