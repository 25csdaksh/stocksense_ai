"""
MarketMind AI — News Intelligence Specialist Agent.
Phase 6.9: Analyzes verified breaking headlines, sentiment scores, event categorizations,
and timeline developments with strict citation URL provenance and deduplication.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchEvidence,
    EvidenceProvenance,
    Citation,
)
from app.services.news_service import NewsService
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class NewsIntelligenceAgent:
    """Specialist agent parsing verified news articles, sentiment trends, and event impacts."""

    def __init__(self):
        self.service = NewsService()

    async def run(self, symbols: List[str], limit: int = 5) -> List[ResearchEvidence]:
        """Collects structured news headlines and sentiment evidence for the target symbols."""
        evidence_list: List[ResearchEvidence] = []

        if not symbols:
            return evidence_list

        for raw_sym in symbols:
            try:
                norm = normalize_symbol(raw_sym)
                canonical = norm.canonical_symbol

                news_res = await self.service.get_news_for_ticker(canonical, limit=limit)
                articles = news_res.get("articles", [])
                sentiment_ov = news_res.get("sentiment_summary") or {}

                seen_hashes = set()
                top_articles = []

                for art in articles:
                    ch = art.get("content_hash")
                    if ch and ch in seen_hashes:
                        continue
                    if ch:
                        seen_hashes.add(ch)

                    top_articles.append({
                        "title": art.get("title"),
                        "source": art.get("source"),
                        "url": art.get("url"),
                        "published_at": art.get("published_at"),
                        "sentiment": art.get("sentiment_label") or art.get("sentiment"),
                        "sentiment_score": art.get("sentiment_score"),
                        "event_type": art.get("event_type", "GENERAL_FINANCIAL"),
                        "summary": art.get("summary") or art.get("description", "")
                    })

                data_status = articles[0].get("data_status", "DEMO") if articles else "DEMO"
                prov_enum = EvidenceProvenance.LIVE if str(data_status).upper() == "LIVE" else EvidenceProvenance.DEMO

                # 1. Aggregate Sentiment Evidence
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="NEWS",
                        symbol=canonical,
                        metric="news_sentiment_summary",
                        value={
                            "articles_analyzed": len(top_articles),
                            "dominant_sentiment": sentiment_ov.get("dominant_sentiment", "NEUTRAL"),
                            "sentiment_score": sentiment_ov.get("sentiment_score", 0.0),
                            "positive_count": sentiment_ov.get("positive_count", 0),
                            "negative_count": sentiment_ov.get("negative_count", 0),
                            "neutral_count": sentiment_ov.get("neutral_count", 0),
                        },
                        source="NewsIntelligencePipeline",
                        provenance=EvidenceProvenance.MODEL_DERIVED,
                        confidence=0.90
                    )
                )

                # 2. Key Headline Citations & Evidence
                for art_item in top_articles[:3]:
                    cite = Citation(
                        citation_id=f"cite_{uuid.uuid4().hex[:6]}",
                        source_type="NEWS_ARTICLE",
                        source_name=art_item.get("source", "Financial News Feed"),
                        source_url=art_item.get("url"),
                        published_at=art_item.get("published_at"),
                        excerpt=art_item.get("title")
                    )

                    evidence_list.append(
                        ResearchEvidence(
                            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                            category="NEWS",
                            symbol=canonical,
                            metric="headline_event",
                            value=art_item,
                            source=art_item.get("source", "NewsProvider"),
                            timestamp=art_item.get("published_at") or datetime.now(timezone.utc).isoformat(),
                            provenance=prov_enum,
                            confidence=0.95,
                            citation=cite
                        )
                    )

            except Exception as ex:
                logger.warning(f"NewsIntelligenceAgent error for {raw_sym}: {ex}")
                evidence_list.append(
                    ResearchEvidence(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        category="NEWS",
                        symbol=raw_sym,
                        metric="news_status",
                        value={"status": "UNAVAILABLE", "error": str(ex)[:80]},
                        source="NewsProvider",
                        provenance=EvidenceProvenance.UNAVAILABLE,
                        confidence=0.2
                    )
                )

        return evidence_list


news_agent = NewsIntelligenceAgent()
