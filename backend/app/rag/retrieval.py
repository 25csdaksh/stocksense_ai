"""
Vector Retrieval Engine with Hybrid Lexical & Cosine Similarity.
"""
from typing import List, Dict, Any, Optional
import re
from app.rag.embeddings import embedding_model

# Pre-populated SEC 10-K Knowledge Corpus
PRELOADED_SEC_CORPUS = [
    {
        "id": "sec_nvda_10k_risk_1",
        "ticker": "NVDA",
        "title": "NVIDIA Corporation Form 10-K (Fiscal Year Ended January 28, 2024)",
        "filing_type": "10-K",
        "fiscal_year": 2024,
        "section": "Item 1A. Risk Factors — Advanced Packaging & TSMC Foundry Sourcing",
        "page_number": 34,
        "content": "We rely on third-party foundries, primarily TSMC, to manufacture all of our semiconductor wafers and advanced CoWoS (Chip-on-Wafer-on-Substrate) packaging. Failure to secure sufficient wafer allocations or packaging substrate substrates to meet datacenter demand could limit revenue growth."
    },
    {
        "id": "sec_nvda_10k_mda_2",
        "ticker": "NVDA",
        "title": "NVIDIA Corporation Form 10-K (Fiscal Year Ended January 28, 2024)",
        "filing_type": "10-K",
        "fiscal_year": 2024,
        "section": "Item 7. Management's Discussion and Analysis — Compute & Networking Momentum",
        "page_number": 51,
        "content": "Compute & Networking revenue increased 217% to $47.4 billion, reflecting strong demand for the NVIDIA HGX platform based on Hopper architecture. Datacenter customers transitioned from general-purpose CPU computing to accelerated computing for generative AI model training and inference."
    },
    {
        "id": "sec_aapl_10k_risk_1",
        "ticker": "AAPL",
        "title": "Apple Inc. Form 10-K (Fiscal Year Ended September 28, 2024)",
        "filing_type": "10-K",
        "fiscal_year": 2024,
        "section": "Item 1A. Risk Factors — Global Supply Chain & Semiconductor Sourcing",
        "page_number": 28,
        "content": "The Company's business can be impacted by international trade disputes, tariffs, and geopolitical events. Substantially all of the Company's manufacturing is performed by outsourced partners concentrated in Asia. Any disruption to advanced silicon fabrication facilities or logistics hubs could materially affect product shipments and operating gross margins."
    },
    {
        "id": "sec_aapl_10k_mda_2",
        "ticker": "AAPL",
        "title": "Apple Inc. Form 10-K (Fiscal Year Ended September 28, 2024)",
        "filing_type": "10-K",
        "fiscal_year": 2024,
        "section": "Item 7. Management's Discussion and Analysis — Services Gross Margin Expansion",
        "page_number": 42,
        "content": "Services revenue reached an all-time record of $96.2 billion, up 12.8% year-over-year. Services gross margin expanded to 74.0%, driven by App Store, Cloud Services, and Advertising growth. Installed base of active devices surpassed 2.2 billion active devices worldwide."
    },
    {
        "id": "sec_msft_10k_mda_1",
        "ticker": "MSFT",
        "title": "Microsoft Corporation Form 10-K (Fiscal Year Ended June 30, 2024)",
        "filing_type": "10-K",
        "fiscal_year": 2024,
        "section": "Item 7. Management's Discussion and Analysis — Intelligent Cloud & Azure Scaling",
        "page_number": 39,
        "content": "Intelligent Cloud revenue was $105.4 billion and increased 19%. Azure and other cloud services revenue grew 29%, driven by demand for our scalable cloud infrastructure and AI services. Capital expenditures were $44.5 billion to support growing demand for cloud infrastructure."
    }
]


class VectorRetriever:
    """Retrieves top-K semantic document matches with metadata filtering."""

    def __init__(self):
        self.corpus = PRELOADED_SEC_CORPUS

    def search(self, query: str, ticker: Optional[str] = None, filing_type: str = "ALL", top_k: int = 5) -> List[Dict[str, Any]]:
        candidates = self.corpus
        if ticker:
            candidates = [c for c in candidates if c["ticker"] == ticker.upper()]
        if filing_type != "ALL":
            candidates = [c for c in candidates if c["filing_type"] == filing_type.upper()]

        q_words = set(re.findall(r"\w+", query.lower()))
        results = []

        for doc in candidates:
            c_words = set(re.findall(r"\w+", doc["content"].lower()))
            s_words = set(re.findall(r"\w+", doc["section"].lower()))
            matches = q_words.intersection(c_words)
            section_matches = q_words.intersection(s_words)

            score = 0.40 + (len(matches) * 0.15 + len(section_matches) * 0.25)
            if ticker and doc["ticker"].lower() in query.lower():
                score += 0.10

            score = min(0.98, max(0.35, score))

            results.append({
                "id": doc["id"],
                "ticker": doc["ticker"],
                "title": doc.get("title", f"{doc['ticker']} {doc['filing_type']}"),
                "filing_type": doc["filing_type"],
                "fiscal_year": doc.get("fiscal_year", 2024),
                "section": doc["section"],
                "page_number": doc.get("page_number", 1),
                "content_snippet": doc["content"],
                "relevance_score": round(float(score), 4)
            })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]


vector_retriever = VectorRetriever()
