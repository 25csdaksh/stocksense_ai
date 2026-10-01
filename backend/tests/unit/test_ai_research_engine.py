"""
MarketMind AI — Phase 6.9 Unit Tests: MultiAgentResearchEngine & Streaming Lifecycle.
"""
import json
import pytest
from app.ai.engine import multi_agent_engine
from app.ai.models import ResearchDepth, ResearchIntent


@pytest.mark.asyncio
async def test_research_engine_execution_standard():
    result = await multi_agent_engine.execute_research(
        query="Analyze RELIANCE.NS price behavior and valuation",
        depth=ResearchDepth.STANDARD,
        session_id="test_engine_sess_01"
    )

    assert "query" in result
    assert "intent" in result
    assert "research_plan" in result
    assert "execution_summary" in result
    assert "report" in result
    assert "citations" in result
    assert "provenance" in result
    assert "limitations" in result

    # Check execution summary and graph
    exec_summary = result["execution_summary"]
    assert "evidence_graph" in exec_summary
    assert exec_summary["total_evidence_collected"] > 0

    # Check report fields
    report = result["report"]
    assert report["executive_summary"] is not None
    assert report["research_conclusion"] is not None
    assert "confidence_level" in report


@pytest.mark.asyncio
async def test_research_engine_streaming_lifecycle():
    events = []
    async for raw_sse in multi_agent_engine.stream_research(
        query="Compare RELIANCE.NS and TCS.NS across risk and momentum",
        depth=ResearchDepth.STANDARD,
        session_id="test_stream_sess_01"
    ):
        events.append(raw_sse)

    assert len(events) > 0

    # Check expected SSE event lifecycle tags
    has_started = any("RESEARCH_STARTED" in ev for ev in events)
    has_plan = any("PLAN_CREATED" in ev for ev in events)
    has_evidence = any("EVIDENCE_COLLECTED" in ev for ev in events)
    has_validation = any("VALIDATION_COMPLETED" in ev for ev in events)
    has_completed = any("RESEARCH_COMPLETED" in ev for ev in events)

    assert has_started is True
    assert has_plan is True
    assert has_evidence is True
    assert has_validation is True
    assert has_completed is True


@pytest.mark.asyncio
async def test_research_engine_partial_failure_resilience(monkeypatch):
    from app.ai.agents.news_agent import news_agent

    async def fail_news(*args, **kwargs):
        raise RuntimeError("News feed timeout or unavailable")

    monkeypatch.setattr(news_agent, "run", fail_news)

    # Engine must still succeed and produce report with available evidence
    result = await multi_agent_engine.execute_research(
        query="What are the latest news headlines and sentiment for INFY.NS?",
        depth=ResearchDepth.STANDARD,
        session_id="test_partial_failure_sess"
    )

    assert result["report"] is not None
    assert result["report"]["research_conclusion"] is not None
    # Check that failed task is noted
    tasks = result["research_plan"]["tasks"]
    news_task = [t for t in tasks if t["agent"] == "news_agent"]
    assert len(news_task) == 1
    assert news_task[0]["status"] == "FAILED"
