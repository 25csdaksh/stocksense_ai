"""
MarketMind AI — Financial News Validation & Content Sanitizer.
Phase 6.7: Strict input validation, URL normalization, hash fingerprinting,
and XSS / HTML sanitization for financial news articles.
"""
import re
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse
from app.providers.news.models import NewsArticleData, NewsDataSource, NewsDataStatus


# Dangerous HTML tag patterns for sanitization
HTML_TAG_REGEX = re.compile(r"<[^>]+>", re.IGNORECASE)
SCRIPT_TAG_REGEX = re.compile(r"<script[\s\S]*?>[\s\S]*?<\/script>", re.IGNORECASE)
IFRAME_TAG_REGEX = re.compile(r"<iframe[\s\S]*?>[\s\S]*?<\/iframe>", re.IGNORECASE)
JAVASCRIPT_URL_REGEX = re.compile(r"^javascript:", re.IGNORECASE)


def sanitize_text(text: Optional[str]) -> str:
    """
    Strips dangerous HTML, script tags, iframes, and excessive whitespace
    to ensure safe rendering in frontend news components.
    """
    if not text:
        return ""
    # Strip script and iframe blocks entirely
    clean = SCRIPT_TAG_REGEX.sub("", text)
    clean = IFRAME_TAG_REGEX.sub("", clean)
    # Strip remaining HTML tags
    clean = HTML_TAG_REGEX.sub("", clean)
    # Normalize excessive spaces/newlines
    clean = " ".join(clean.split())
    return clean.strip()


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """Validates and sanitizes news URLs, rejecting javascript: and malformed protocols."""
    if not url or url.strip() == "#":
        return None
    url = url.strip()
    if JAVASCRIPT_URL_REGEX.match(url):
        return None
    try:
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return url
    except Exception:
        pass
    return None


def generate_article_fingerprint(headline: str, source: str, published_at: str) -> str:
    """Generates a deterministic SHA-256 fingerprint for deduplication."""
    norm_headline = " ".join(headline.lower().split())
    norm_source = source.strip().lower()
    raw = f"{norm_headline}|{norm_source}|{published_at.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class NewsValidator:
    """Strict validator for incoming provider news articles."""

    @staticmethod
    def validate_and_sanitize(raw: Dict[str, Any]) -> Tuple[bool, Optional[NewsArticleData], Optional[str]]:
        """
        Validates raw news dictionary, sanitizes content, checks required fields,
        and constructs a validated NewsArticleData model.
        """
        headline = raw.get("headline") or raw.get("title")
        if not headline or not isinstance(headline, str) or len(headline.strip()) < 5:
            return False, None, "Invalid or missing headline (minimum 5 chars required)"

        source = raw.get("source") or "Financial Intelligence Feed"
        if not isinstance(source, str) or len(source.strip()) < 2:
            return False, None, "Invalid news source identifier"

        summary = raw.get("summary") or headline
        if not isinstance(summary, str):
            summary = str(summary)

        # Sanitize text
        clean_headline = sanitize_text(headline)
        clean_summary = sanitize_text(summary)
        clean_content = sanitize_text(raw.get("content")) if raw.get("content") else None
        clean_url = sanitize_url(raw.get("url"))

        published_at = raw.get("published_at") or "Just now"
        article_id = str(raw.get("id") or f"art-{generate_article_fingerprint(clean_headline, source, str(published_at))[:12]}")
        content_hash = generate_article_fingerprint(clean_headline, source, str(published_at))

        # Validate numeric bounds
        sentiment_score = float(raw.get("sentiment_score", 0.0))
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        impact_score = float(raw.get("impact_score", 0.5))
        impact_score = max(0.0, min(1.0, impact_score))

        relevance_score = float(raw.get("relevance_score", 0.8))
        relevance_score = max(0.0, min(1.0, relevance_score))

        # Provenance
        data_source = raw.get("data_source") or NewsDataSource.DEMO
        if isinstance(data_source, str):
            try:
                data_source = NewsDataSource(data_source)
            except ValueError:
                data_source = NewsDataSource.OTHER

        data_status = raw.get("data_status") or NewsDataStatus.DEMO
        if isinstance(data_status, str):
            try:
                data_status = NewsDataStatus(data_status)
            except ValueError:
                data_status = NewsDataStatus.DEMO

        # Symbols extraction & formatting
        symbols = raw.get("symbols") or []
        if isinstance(symbols, str):
            symbols = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        elif isinstance(symbols, list):
            symbols = [str(s).strip().upper() for s in symbols if str(s).strip()]

        ticker = raw.get("ticker")
        if ticker:
            ticker = str(ticker).strip().upper()
            if ticker not in symbols:
                symbols.insert(0, ticker)
        elif symbols:
            ticker = symbols[0]

        article = NewsArticleData(
            id=article_id,
            headline=clean_headline,
            title=clean_headline,
            summary=clean_summary,
            content=clean_content,
            url=clean_url,
            source=source.strip(),
            author=raw.get("author"),
            published_at=str(published_at),
            updated_at=raw.get("updated_at"),
            language=raw.get("language", "en"),
            country=raw.get("country", "IN"),
            market=raw.get("market", "INDIA"),
            ticker=ticker,
            symbols=symbols,
            companies=raw.get("companies") or [],
            sectors=raw.get("sectors") or ([] if not raw.get("sector") else [raw.get("sector")]),
            sector=raw.get("sector"),
            topics=raw.get("topics") or [],
            category=raw.get("category") or "MARKET",
            event_type=raw.get("event_type") or "OTHER",
            event_confidence=float(raw.get("event_confidence", 0.85)),
            sentiment=raw.get("sentiment") or raw.get("sentiment_label") or "NEUTRAL",
            sentiment_label=str(raw.get("sentiment_label") or "NEUTRAL").upper(),
            sentiment_score=sentiment_score,
            sentiment_confidence=float(raw.get("sentiment_confidence", 0.80)),
            relevance_score=relevance_score,
            impact_score=impact_score,
            impact_direction=raw.get("impact_direction") or "NEUTRAL",
            impact_horizon=raw.get("impact_horizon") or "SHORT_TERM",
            impact_scope=raw.get("impact_scope") or "STOCK",
            data_source=data_source,
            data_status=data_status,
            content_hash=content_hash
        )

        return True, article, None


news_validator = NewsValidator()
