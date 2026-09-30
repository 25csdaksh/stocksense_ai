"""
Unit Tests: Financial News Normalized Models, Validator, XSS Sanitizer, and NLP Intelligence Engine.
Phase 6.7: Comprehensive verification of entity linking, sentiment scoring, event classification, and provenance.
"""
import pytest
from app.providers.news.models import (
    NewsArticleData,
    NewsCategory,
    NewsEventType,
    SentimentLabel,
    ImpactDirection,
    ImpactHorizon,
    ImpactScope,
    NewsDataSource,
    NewsDataStatus,
    SectorSentimentSummary,
    NewsSentimentAggregation,
)
from app.providers.news.validator import news_validator, sanitize_text, sanitize_url, generate_article_fingerprint
from app.analytics.news_nlp_engine import news_nlp_engine


def test_article_validation_and_model():
    raw = {
        "id": "test_nvda_001",
        "headline": "NVIDIA Reports Record Q3 Datacenter Revenue Growth",
        "summary": "Operating margins expanded as Blackwell GPU shipments accelerated.",
        "source": "Bloomberg",
        "url": "https://bloomberg.com/news/nvda-q3",
        "published_at": "2026-03-30T10:00:00Z",
        "ticker": "NVDA",
        "symbols": ["NVDA"],
        "sentiment_score": 0.85,
        "impact_score": 0.90,
        "data_source": "DEMO",
        "data_status": "DEMO"
    }
    valid, article, err = news_validator.validate_and_sanitize(raw)
    assert valid is True
    assert article is not None
    assert article.ticker == "NVDA"
    assert article.title == article.headline
    assert article["sentiment_score"] == 0.85
    assert "headline" in article
    assert article.get("source") == "Bloomberg"


def test_xss_and_script_sanitization():
    dirty_headline = "<script>alert('xss')</script>Reliance Industries Signs <b>New</b> Green Energy Deal"
    clean = sanitize_text(dirty_headline)
    assert "<script>" not in clean
    assert "alert" not in clean
    assert "<b>" not in clean
    assert clean == "Reliance Industries Signs New Green Energy Deal"

    dirty_url = "javascript:alert('malicious')"
    assert sanitize_url(dirty_url) is None
    assert sanitize_url("https://reuters.com/news/123") == "https://reuters.com/news/123"


def test_article_fingerprint_deduplication():
    h1 = generate_article_fingerprint("TCS Wins $1B Deal", "Reuters", "2026-03-30 10:00:00")
    h2 = generate_article_fingerprint("  tcs wins $1b deal  ", "  reuters  ", "2026-03-30 10:00:00")
    h3 = generate_article_fingerprint("Infosys Guidance Upgrade", "Reuters", "2026-03-30 10:00:00")

    assert h1 == h2
    assert h1 != h3


def test_entity_linking_indian_and_us():
    text_in = "Reliance Industries and Tata Consultancy Services lead gains on the NIFTY 50 today as RBI holds repo rate."
    symbols, companies, sectors = news_nlp_engine.link_entities(text_in)

    assert "RELIANCE.NS" in symbols
    assert "TCS.NS" in symbols
    assert "^NSEI" in symbols
    assert "Energy & Petrochemicals" in sectors or "Information Technology" in sectors

    text_us = "Apple and NVIDIA announce collaborative AI silicon platform for Microsoft Azure."
    symbols_us, companies_us, sectors_us = news_nlp_engine.link_entities(text_us)
    assert "AAPL" in symbols_us
    assert "NVDA" in symbols_us
    assert "MSFT" in symbols_us


def test_sentiment_scoring():
    pos_text = "TCS profits surge 24% to record high with strong margin growth and new dividend hike."
    label_p, score_p, conf_p = news_nlp_engine.analyze_sentiment(pos_text)
    assert label_p == SentimentLabel.POSITIVE
    assert score_p > 0.5
    assert conf_p >= 0.75

    neg_text = "Automaker faces severe revenue decline and probe following regulatory penalty."
    label_n, score_n, conf_n = news_nlp_engine.analyze_sentiment(neg_text)
    assert label_n == SentimentLabel.NEGATIVE
    assert score_n < -0.4

    neu_text = "Federal Reserve minutes describe data-dependent approach to policy normalization."
    label_neu, score_neu, _ = news_nlp_engine.analyze_sentiment(neu_text)
    assert abs(score_neu) <= 0.35


def test_event_classification():
    ev_earnings, _ = news_nlp_engine.classify_event("Infosys announces Q4 earnings and net profit beat.")
    assert ev_earnings == NewsEventType.EARNINGS

    ev_div, _ = news_nlp_engine.classify_event("Board recommends final dividend of Rs 28 per equity share.")
    assert ev_div == NewsEventType.DIVIDEND

    ev_mna, _ = news_nlp_engine.classify_event("Tata Motors enters agreement to acquire European battery manufacturer.")
    assert ev_mna == NewsEventType.M_AND_A

    ev_mgmt, _ = news_nlp_engine.classify_event("Chief Executive Officer steps down as board appoints new managing director.")
    assert ev_mgmt == NewsEventType.MANAGEMENT_CHANGE


def test_impact_and_relevance_scoring():
    direction, impact_score, horizon, scope = news_nlp_engine.evaluate_impact(
        sentiment_score=0.85,
        event_type=NewsEventType.EARNINGS,
        symbols_count=1
    )
    assert direction == ImpactDirection.POSITIVE
    assert 0.0 <= impact_score <= 1.0
    assert horizon == ImpactHorizon.SHORT_TERM
    assert scope == ImpactScope.STOCK

    rel_score = news_nlp_engine.compute_relevance(
        target_symbol="RELIANCE.NS",
        article_symbols=["RELIANCE.NS", "TCS.NS"],
        headline="Reliance Approves Bonus Issue",
        summary="Reliance Industries rewards shareholders."
    )
    assert rel_score >= 0.85


def test_data_provenance_preservation():
    raw_demo = {
        "id": "art-demo-1",
        "headline": "Sample Market Update",
        "summary": "Informational summary.",
        "source": "Demo Provider",
        "data_source": "DEMO",
        "data_status": "DEMO"
    }
    valid, art, _ = news_validator.validate_and_sanitize(raw_demo)
    assert art.data_source == NewsDataSource.DEMO
    assert art.data_status == NewsDataStatus.DEMO
    assert art.data_status.value != "LIVE"
