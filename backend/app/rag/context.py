"""
RAG Context Builder & Citation Formatter.
"""
from typing import List, Dict, Any


class ContextBuilder:
    """Formats retrieved regulatory citations into LLM prompt contexts."""

    @staticmethod
    def build_context(citations: List[Dict[str, Any]]) -> str:
        if not citations:
            return "No regulatory document citations retrieved for this query."

        lines = ["### Verified SEC Regulatory Disclosures:\n"]
        for c in citations:
            lines.append(
                f"- **[{c['ticker']} {c['filing_type']} FY{c['fiscal_year']} — {c['section']} (p.{c['page_number']})]**:\n"
                f"  \"{c['content_snippet']}\"\n"
            )
        return "\n".join(lines)
