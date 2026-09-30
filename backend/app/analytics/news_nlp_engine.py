"""
MarketMind AI — Deterministic Financial News NLP & Intelligence Engine.
Phase 6.7: Keyword-based & financial taxonomy sentiment scoring, event classification,
entity linking (symbols, companies, sectors), and multi-horizon market impact evaluation.
"""
import re
from typing import Dict, Any, List, Tuple, Optional
from app.providers.news.models import (
    NewsCategory,
    NewsEventType,
    SentimentLabel,
    ImpactDirection,
    ImpactHorizon,
    ImpactScope,
)
from app.providers.market_data.symbol_normalizer import symbol_normalizer


# =========================================================================
# Financial Entity Dictionaries
# =========================================================================

COMPANY_ENTITY_MAP = {
    # Indian Equities
    "reliance": ("RELIANCE.NS", "Reliance Industries Ltd", "Energy & Petrochemicals"),
    "jio": ("RELIANCE.NS", "Reliance Industries Ltd", "Telecommunications"),
    "tcs": ("TCS.NS", "Tata Consultancy Services", "Information Technology"),
    "tata consultancy": ("TCS.NS", "Tata Consultancy Services", "Information Technology"),
    "infosys": ("INFY.NS", "Infosys Ltd", "Information Technology"),
    "infy": ("INFY.NS", "Infosys Ltd", "Information Technology"),
    "hdfc bank": ("HDFCBANK.NS", "HDFC Bank Ltd", "Banking & Financials"),
    "hdfc": ("HDFCBANK.NS", "HDFC Bank Ltd", "Banking & Financials"),
    "icici bank": ("ICICIBANK.NS", "ICICI Bank Ltd", "Banking & Financials"),
    "icici": ("ICICIBANK.NS", "ICICI Bank Ltd", "Banking & Financials"),
    "state bank of india": ("SBIN.NS", "State Bank of India", "Banking & Financials"),
    "sbi": ("SBIN.NS", "State Bank of India", "Banking & Financials"),
    "itc": ("ITC.NS", "ITC Limited", "Consumer Goods & FMCG"),
    "tata motors": ("TATAMOTORS.NS", "Tata Motors Ltd", "Automotive & Mobility"),
    "maruti": ("MARUTI.NS", "Maruti Suzuki India", "Automotive & Mobility"),
    "ongc": ("ONGC.NS", "Oil and Natural Gas Corp", "Energy & Petrochemicals"),
    "bharti airtel": ("BHARTIARTL.NS", "Bharti Airtel Ltd", "Telecommunications"),
    "airtel": ("BHARTIARTL.NS", "Bharti Airtel Ltd", "Telecommunications"),

    # Benchmark Indices & Macro
    "nifty 50": ("^NSEI", "NIFTY 50 Index", "Benchmark Indices"),
    "nifty": ("^NSEI", "NIFTY 50 Index", "Benchmark Indices"),
    "sensex": ("^BSESN", "BSE SENSEX", "Benchmark Indices"),
    "nifty bank": ("^NSEBANK", "NIFTY Bank Index", "Banking & Financials"),
    "nifty it": ("^CNXIT", "NIFTY IT Index", "Information Technology"),
    "rbi": ("^NSEI", "Reserve Bank of India", "Macroeconomic Policy"),

    # US Equities
    "apple": ("AAPL", "Apple Inc.", "Technology Hardware"),
    "microsoft": ("MSFT", "Microsoft Corp.", "Cloud & Enterprise Software"),
    "azure": ("MSFT", "Microsoft Corp.", "Cloud Computing"),
    "nvidia": ("NVDA", "NVIDIA Corp.", "Semiconductors & AI"),
    "blackwell": ("NVDA", "NVIDIA Corp.", "Semiconductors & AI"),
    "amazon": ("AMZN", "Amazon.com Inc.", "E-Commerce & Cloud"),
    "aws": ("AMZN", "Amazon.com Inc.", "Cloud Computing"),
    "google": ("GOOGL", "Alphabet Inc.", "Digital Media & Search"),
    "alphabet": ("GOOGL", "Alphabet Inc.", "Digital Media & Search"),
    "tesla": ("TSLA", "Tesla Inc.", "Automotive & Clean Energy"),
    "meta": ("META", "Meta Platforms Inc.", "Social Media & Metaverse"),
    "federal reserve": ("SPY", "Federal Reserve Board", "Macroeconomic Policy"),
    "fomc": ("SPY", "Federal Open Market Committee", "Macroeconomic Policy"),
}


# =========================================================================
# Sentiment Keywords & Weights
# =========================================================================

POSITIVE_TERMS = {
    "surge": 0.8, "soar": 0.9, "record high": 0.95, "beat": 0.75, "outperform": 0.8,
    "jump": 0.65, "gain": 0.5, "upgrade": 0.85, "expansion": 0.6, "growth": 0.55,
    "profit up": 0.85, "revenue up": 0.8, "dividend hike": 0.8, "buyback": 0.75,
    "strong demand": 0.7, "robust": 0.65, "secures contract": 0.85, "accelerates": 0.6,
    "breakthrough": 0.9, "all-time high": 0.95, "rally": 0.7, "bullish": 0.8
}

NEGATIVE_TERMS = {
    "slump": -0.8, "plunge": -0.9, "drop": -0.6, "fall": -0.5, "miss": -0.75,
    "downgrade": -0.85, "underperform": -0.8, "loss": -0.7, "profit down": -0.85,
    "revenue decline": -0.8, "lawsuit": -0.75, "probe": -0.8, "investigation": -0.85,
    "fraud": -0.95, "penalty": -0.8, "fine": -0.65, "inflation spike": -0.7,
    "rate hike": -0.6, "weak demand": -0.7, "margin compression": -0.75,
    "layoffs": -0.65, "default": -0.95, "bankruptcy": -1.0, "bearish": -0.8
}


# =========================================================================
# Event Classification Rules
# =========================================================================

EVENT_PATTERNS = [
    (NewsEventType.EARNINGS, re.compile(r"\b(earnings|q[1-4]|quarterly (profit|result|loss)|net profit|ebitda|revenue beat|revenue miss)\b", re.I)),
    (NewsEventType.DIVIDEND, re.compile(r"\b(dividend|payout|special dividend|interim dividend)\b", re.I)),
    (NewsEventType.BUYBACK, re.compile(r"\b(buyback|share repurchase|shares repurchase)\b", re.I)),
    (NewsEventType.M_AND_A, re.compile(r"\b(acquire|acquisition|merger|takeover|buyout|deal to buy)\b", re.I)),
    (NewsEventType.MANAGEMENT_CHANGE, re.compile(r"\b(appoints|steps down|resigns|named ceo|named cfo|board changes|executive leadership)\b", re.I)),
    (NewsEventType.REGULATORY_ACTION, re.compile(r"\b(sebi|rbi|sec|regulatory (approval|probe|action|fine|penalty)|antitrust)\b", re.I)),
    (NewsEventType.LEGAL_EVENT, re.compile(r"\b(lawsuit|court|settlement|litigation|patent dispute|legal action)\b", re.I)),
    (NewsEventType.PRODUCT_LAUNCH, re.compile(r"\b(launches|unveils|reveals|product lineup|next-gen|rollout|blackwell|chip)\b", re.I)),
    (NewsEventType.PARTNERSHIP, re.compile(r"\b(partnership|alliance|collaboration|teams up with|joint venture)\b", re.I)),
    (NewsEventType.RATING_CHANGE, re.compile(r"\b(upgrades|downgrades|initiates coverage|price target|analyst rating)\b", re.I)),
    (NewsEventType.MACRO_EVENT, re.compile(r"\b(repo rate|fomc|federal reserve|cpi inflation|gdp growth|crude oil|monetary policy)\b", re.I)),
    (NewsEventType.FUNDRAISING, re.compile(r"\b(fundraise|ipo|qip|rights issue|debt offering|bond issuance)\b", re.I)),
]


# =========================================================================
# Category Classification Rules
# =========================================================================

CATEGORY_PATTERNS = [
    (NewsCategory.EARNINGS, re.compile(r"\b(earnings|q[1-4]|quarterly|pat|ebitda|gross margin)\b", re.I)),
    (NewsCategory.REGULATORY, re.compile(r"\b(sebi|rbi|sec|regulator|compliance|audit|antitrust)\b", re.I)),
    (NewsCategory.M_AND_A, re.compile(r"\b(acquisition|merger|takeover|buyout)\b", re.I)),
    (NewsCategory.CORPORATE_ACTION, re.compile(r"\b(dividend|buyback|bonus issue|stock split)\b", re.I)),
    (NewsCategory.TECHNOLOGY, re.compile(r"\b(ai|cloud|semiconductor|gpu|software|cybersecurity|chip)\b", re.I)),
    (NewsCategory.MACRO, re.compile(r"\b(inflation|repo rate|fomc|fed|gdp|monetary policy|crude)\b", re.I)),
    (NewsCategory.ANALYST, re.compile(r"\b(upgrade|downgrade|price target|overweight|buy rating)\b", re.I)),
    (NewsCategory.LEGAL, re.compile(r"\b(lawsuit|court|litigation|patent|verdict)\b", re.I)),
    (NewsCategory.MANAGEMENT, re.compile(r"\b(ceo|cfo|resigns|appoints|executive|managing director)\b", re.I)),
]


class NewsNLPEngine:
    """Deterministic NLP and classification engine for financial news intelligence."""

    @classmethod
    def link_entities(
        cls,
        text: str,
        provided_symbols: Optional[List[str]] = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Extracts and links financial symbols, company names, and sectors from headline/body.
        Returns: (symbols, company_names, sectors)
        """
        symbols_set = set()
        companies_set = set()
        sectors_set = set()

        if provided_symbols:
            for s in provided_symbols:
                norm = symbol_normalizer.normalize(s).display_symbol or s
                symbols_set.add(norm)

        text_lower = text.lower()
        for keyword, (sym, comp_name, sec_name) in COMPANY_ENTITY_MAP.items():
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, text_lower):
                symbols_set.add(sym)
                companies_set.add(comp_name)
                sectors_set.add(sec_name)

        return sorted(list(symbols_set)), sorted(list(companies_set)), sorted(list(sectors_set))

    @classmethod
    def analyze_sentiment(cls, text: str) -> Tuple[SentimentLabel, float, float]:
        """
        Computes sentiment polarity (-1.0 to +1.0) and confidence (0.0 to 1.0).
        Returns: (label, score, confidence)
        """
        text_lower = text.lower()
        pos_scores = []
        neg_scores = []

        for term, weight in POSITIVE_TERMS.items():
            if re.search(rf"\b{re.escape(term)}\b", text_lower):
                pos_scores.append(weight)

        for term, weight in NEGATIVE_TERMS.items():
            if re.search(rf"\b{re.escape(term)}\b", text_lower):
                neg_scores.append(weight)

        if not pos_scores and not neg_scores:
            return SentimentLabel.NEUTRAL, 0.0, 0.70

        if pos_scores and neg_scores:
            net = sum(pos_scores) + sum(neg_scores)
            score = max(-1.0, min(1.0, net / (len(pos_scores) + len(neg_scores))))
            label = SentimentLabel.MIXED if abs(score) < 0.15 else (
                SentimentLabel.POSITIVE if score > 0 else SentimentLabel.NEGATIVE
            )
            return label, round(score, 3), 0.75

        if pos_scores:
            score = min(1.0, sum(pos_scores) / len(pos_scores))
            return SentimentLabel.POSITIVE, round(score, 3), 0.85

        score = max(-1.0, sum(neg_scores) / len(neg_scores))
        return SentimentLabel.NEGATIVE, round(score, 3), 0.85

    @classmethod
    def classify_event(cls, text: str) -> Tuple[NewsEventType, float]:
        """Classifies financial event type and outputs confidence."""
        for ev_type, pattern in EVENT_PATTERNS:
            if pattern.search(text):
                return ev_type, 0.90
        return NewsEventType.OTHER, 0.60

    @classmethod
    def classify_category(cls, text: str) -> NewsCategory:
        """Classifies article into standard financial news category."""
        for category, pattern in CATEGORY_PATTERNS:
            if pattern.search(text):
                return category
        return NewsCategory.MARKET

    @classmethod
    def evaluate_impact(
        cls,
        sentiment_score: float,
        event_type: NewsEventType,
        symbols_count: int
    ) -> Tuple[ImpactDirection, float, ImpactHorizon, ImpactScope]:
        """
        Estimates market impact direction, magnitude score (0-1), horizon, and scope.
        """
        if sentiment_score > 0.20:
            direction = ImpactDirection.POSITIVE
        elif sentiment_score < -0.20:
            direction = ImpactDirection.NEGATIVE
        elif abs(sentiment_score) <= 0.20 and sentiment_score != 0:
            direction = ImpactDirection.MIXED
        else:
            direction = ImpactDirection.NEUTRAL

        # Event-based baseline impact weight
        event_weights = {
            NewsEventType.EARNINGS: 0.85,
            NewsEventType.GUIDANCE_CHANGE: 0.90,
            NewsEventType.M_AND_A: 0.90,
            NewsEventType.DIVIDEND: 0.70,
            NewsEventType.BUYBACK: 0.75,
            NewsEventType.MANAGEMENT_CHANGE: 0.80,
            NewsEventType.REGULATORY_ACTION: 0.85,
            NewsEventType.MACRO_EVENT: 0.90,
            NewsEventType.LEGAL_EVENT: 0.75,
            NewsEventType.PRODUCT_LAUNCH: 0.70,
            NewsEventType.RATING_CHANGE: 0.75,
        }
        base_impact = event_weights.get(event_type, 0.50)
        final_impact = round(min(1.0, base_impact * (0.5 + 0.5 * abs(sentiment_score))), 2)

        if event_type in (NewsEventType.MACRO_EVENT,):
            scope = ImpactScope.MACRO
            horizon = ImpactHorizon.MEDIUM_TERM
        elif event_type in (NewsEventType.M_AND_A, NewsEventType.MANAGEMENT_CHANGE):
            scope = ImpactScope.STOCK
            horizon = ImpactHorizon.LONG_TERM
        elif event_type in (NewsEventType.EARNINGS, NewsEventType.GUIDANCE_CHANGE):
            scope = ImpactScope.STOCK
            horizon = ImpactHorizon.SHORT_TERM
        else:
            scope = ImpactScope.STOCK if symbols_count <= 2 else ImpactScope.SECTOR
            horizon = ImpactHorizon.SHORT_TERM

        return direction, final_impact, horizon, scope

    @classmethod
    def compute_relevance(
        cls,
        target_symbol: Optional[str],
        article_symbols: List[str],
        headline: str,
        summary: str
    ) -> float:
        """Computes deterministic relevance score (0.0 to 1.0) of article for a given symbol."""
        if not target_symbol or not article_symbols:
            return 0.70

        target_norm = symbol_normalizer.normalize(target_symbol).display_symbol or target_symbol.upper()
        if target_norm in article_symbols:
            # First symbol is primary match
            if article_symbols[0] == target_norm:
                return 0.95
            return 0.85

        # Check ticker text presence in headline
        if target_symbol.upper() in headline.upper():
            return 0.80
        if target_symbol.upper() in summary.upper():
            return 0.65

        return 0.40


news_nlp_engine = NewsNLPEngine()
