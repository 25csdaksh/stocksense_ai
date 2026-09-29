"""
Regulatory Compliance & Educational Guardrails Module.
Ensures zero deterministic financial advice, adds mandatory disclaimers,
and validates data integrity.
"""
import re
from typing import Dict, Any, List

FINANCIAL_DISCLAIMER_MD = """
---
> **Disclaimer & Regulatory Notice**: MARKETMIND AI is an academic and quantitative scenario analysis platform designed strictly for educational and analytical research purposes. It does not constitute investment advice, financial planning, or an endorsement to buy or sell any security. All scenario simulations, Value-at-Risk (VaR) projections, and multi-factor models are probabilistic estimates subject to model risk. Past statistical performance is not indicative of future market results.
"""


class FinancialGuardrails:
    """
    Enforces compliance policies on all AI agent outputs and API payloads.
    """

    PROHIBITED_PATTERNS = [
        (r"\b(you must buy|guaranteed to (rise|fall|gain|profit)|100% safe investment|surefire profit)\b", "high-conviction promotional language"),
        (r"\b(strong buy signal guaranteed|target price guaranteed)\b", "guaranteed price target advice"),
    ]

    @classmethod
    def sanitize_agent_output(cls, text: str) -> str:
        """
        Scans AI generated output for prohibited promissory language and sanitizes it,
        then appends the mandatory educational disclaimer.
        """
        sanitized = text
        for pattern, reason in cls.PROHIBITED_PATTERNS:
            sanitized = re.sub(
                pattern,
                "[Probabilistic Model Indicator — Not Investment Advice]",
                sanitized,
                flags=re.IGNORECASE
            )

        if "Disclaimer & Regulatory Notice" not in sanitized:
            sanitized = f"{sanitized.rstrip()}\n\n{FINANCIAL_DISCLAIMER_MD}"

        return sanitized

    @classmethod
    def tag_data_source(cls, is_synthetic: bool = False) -> Dict[str, Any]:
        """Returns standard data authenticity metadata."""
        return {
            "is_synthetic": is_synthetic,
            "data_source": "SYNTHETIC_HIGH_FIDELITY_MOCK" if is_synthetic else "EXCHANGE_MARKET_FEED",
            "provenance_badge": "DEMO / SIMULATED" if is_synthetic else "LIVE MARKET DATA",
            "academic_purpose_only": True
        }
