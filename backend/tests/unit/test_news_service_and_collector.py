"""
Unit & Integration Tests: Financial News Service, Collector, Redis Caching, and Realtime Event Dispatch.
Phase 6.7: Comprehensive testing of provider routing, caching, DB persistence, timelines, and AI tools.
"""
import pytest
from app.services.news_service import news_service
from app.services.news_collector import news_collector
from app.providers.news.factory import get_news_provider
from app.providers.market_data.streaming_events import event_bus, MarketDataEvent, MarketEventType
from app.agents.tools import tool_get_news, tool_get_news_context, tool_get_ai_news_brief


@pytest.mark.asyncio
async def test_provider_routing():
    in_news = await news_service.get_news_for_ticker("RELIANCE.NS", limit=3)
    assert in_news["ticker"] == "RELIANCE.NS"
    assert len(in_news["news_items"]) > 0
    assert "overall_sentiment" in in_news

    us_news = await news_service.get_news_for_ticker("NVDA", limit=3)
    assert us_news["ticker"] == "NVDA"
    assert len(us_news["news_items"]) > 0


@pytest.mark.asyncio
async def test_news_collector_ingest_and_event_bus():
    received_events = []

    async def listener(event: MarketDataEvent):
        if event.event_type == MarketEventType.NEWS_PUBLISHED:
            received_events.append(event)

    event_bus.subscribe(listener)

    raw_article = {
        "id": "test_broadcast_001",
        "headline": "HDFC Bank Reports Strong Credit Growth & Deposit Growth",
        "summary": "Asset quality remains resilient as net interest margin widens.",
        "source": "Financial Express",
        "ticker": "HDFCBANK.NS",
        "symbols": ["HDFCBANK.NS"],
        "data_source": "INDIAN_PROVIDER",
        "data_status": "DEMO"
    }

    res = await news_collector.ingest_article(raw_article, broadcast=True)
    assert res is not None
    assert res.ticker == "HDFCBANK.NS"

    assert len(received_events) >= 1
    ev = received_events[-1]
    assert ev.event_type == MarketEventType.NEWS_PUBLISHED
    assert ev.symbol == "HDFCBANK.NS"
    assert ev.payload["headline"] == "HDFC Bank Reports Strong Credit Growth & Deposit Growth"

    event_bus.unsubscribe(listener)


@pytest.mark.asyncio
async def test_news_collector_telemetry():
    telemetry = news_collector.get_telemetry()
    assert "provider_status" in telemetry
    assert "articles_processed" in telemetry
    assert "duplicates_prevented" in telemetry
    assert telemetry["articles_processed"] >= 0


@pytest.mark.asyncio
async def test_news_timeline_and_anomaly_correlation():
    timeline = await news_service.get_timeline_for_ticker("TCS.NS", limit=5)
    assert isinstance(timeline, list)
    assert len(timeline) > 0
    assert timeline[0].ticker == "TCS.NS"
    assert timeline[0].headline is not None

    anomaly_news = await news_service.get_news_around_anomaly("TCS.NS", window_hours=12)
    assert anomaly_news["symbol"] == "TCS.NS"
    assert "nearby_news" in anomaly_news
    assert len(anomaly_news["nearby_news"]) > 0


@pytest.mark.asyncio
async def test_news_sentiment_aggregation():
    summary = await news_service.get_sentiment_summary(ticker="INFY.NS", limit=10)
    assert summary.ticker == "INFY.NS"
    assert summary.total_articles > 0
    assert summary.overall_sentiment in ("BULLISH", "BEARISH", "NEUTRAL")


@pytest.mark.asyncio
async def test_ai_news_tools():
    # 1. tool_get_news
    news_list = await tool_get_news("AAPL", limit=2)
    assert isinstance(news_list, (list, dict))
    assert len(news_list) > 0

    # 2. tool_get_news_context (Facts vs Classifications vs Analysis)
    ctx = await tool_get_news_context("NVDA", limit=3)
    assert "facts" in ctx
    assert "classifications" in ctx
    assert "analysis" in ctx
    assert "data_provenance" in ctx
    assert len(ctx["facts"]) > 0

    # 3. tool_get_ai_news_brief
    brief = await tool_get_ai_news_brief("NVDA")
    assert brief["ticker"] == "NVDA"
    assert "market_context" in brief
    assert "key_company_news" in brief
    assert "potential_catalysts" in brief
    assert "citations" in brief
