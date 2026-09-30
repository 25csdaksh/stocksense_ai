"""
MarketMind AI — News Intelligence RAG Document Ingestion Pipeline.
Phase 6.7: Cleans, chunks, embeds, and indexes financial news articles into the vector database
with structured citation metadata and deduplication guards.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.core.logging import logger
from app.providers.news.models import NewsArticleData
from app.rag.cleaner import DocumentCleaner
from app.db.vector import vector_repository


class NewsRAGPipeline:
    """Pipelines news articles into searchable vector chunks."""

    def __init__(self):
        self.cleaner = DocumentCleaner()
        self._embedded_hashes: set = set()

    def create_news_chunks(self, article: NewsArticleData) -> List[Dict[str, Any]]:
        """Cleans and chunks article into semantically rich retrieval chunks."""
        full_text = f"{article.headline}\n\n{article.summary}"
        if article.content:
            full_text += f"\n\n{article.content}"

        clean_text = self.cleaner.clean_text(full_text)
        chunk_id = f"news_{article.id}"

        return [{
            "id": chunk_id,
            "content": clean_text,
            "ticker": article.ticker or "MARKET",
            "section": f"News: {article.category.value} / {article.event_type.value}",
            "title": article.headline or article.title,
            "page_number": 1,
            "fiscal_year": 2026,
            "source": article.source,
            "published_at": article.published_at,
            "url": article.url,
            "sentiment_label": article.sentiment_label,
            "sentiment_score": article.sentiment_score,
            "document_type": "NEWS_ARTICLE"
        }]

    async def ingest_news_article(self, article: NewsArticleData) -> bool:
        """Embeds and persists article in vector repository with duplicate avoidance."""
        if not article.content_hash:
            article.content_hash = f"hash_{article.id}"

        if article.content_hash in self._embedded_hashes:
            return True

        chunks = self.create_news_chunks(article)
        try:
            vector_repository.upsert_chunks(chunks)
            self._embedded_hashes.add(article.content_hash)
            return True
        except Exception as e:
            logger.debug(f"[NewsRAGPipeline] Non-fatal vector index error: {e}")
            return False


news_rag_pipeline = NewsRAGPipeline()
