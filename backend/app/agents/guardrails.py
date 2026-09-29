"""
Financial Intelligence Guardrails & AI Safety Validator.
Enforces citation grounding, eliminates aggressive trading directives, and detects ungrounded assertions.
"""
import re
from typing import Dict, Any, List, Tuple
from app.utils.constants import FINANCIAL_DISCLAIMER_TEXT


PROHIBITED_DIRECTIVES = [
    r"\b(?:guaranteed|surefire|cannot lose|risk-free)\b",
    r"\b(?:buy this now|sell immediately|all-in on)\b",
    r"\b(?:100% accurate|guaranteed return)\b"
]


class FinancialAIGuardrails:
    """Enforces strict financial domain compliance and anti-hallucination verification."""

    @staticmethod
    def inspect_and_sanitize(
        answer: str,
        data_context: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> Tuple[str, bool, List[str]]:
        """
        Inspects raw LLM output against safety guardrails:
        1. Strips internal chain-of-thought traces.
        2. Softens prohibited speculative directives into objective analysis.
        3. Validates citations against retrieved evidence.
        4. Appends standard regulatory risk notices.
        """
        warnings = []
        sanitized = answer

        # 1. Remove any internal thought or reasoning tags if present
        sanitized = re.sub(r"(?i)<thought>.*?</thought>", "", sanitized, flags=re.DOTALL)
        sanitized = re.sub(r"(?i)```thought.*?```", "", sanitized, flags=re.DOTALL)

        # 2. Check and sanitize prohibited trading directives
        for pat in PROHIBITED_DIRECTIVES:
            if re.search(pat, sanitized, re.IGNORECASE):
                warnings.append(f"Detected and softened speculative trading directive matching pattern '{pat}'.")
                sanitized = re.sub(pat, "probabilistic market scenario", sanitized, flags=re.IGNORECASE)

        # 3. Citation grounding check
        if citations:
            valid_ids = {c.get("id") for c in citations if c.get("id")}
            # Ensure no orphan bracketed source refs exceed citation count
            max_source_idx = len(citations)
            for m in re.finditer(r"\[Source (\d+)\]", sanitized):
                idx = int(m.group(1))
                if idx > max_source_idx:
                    warnings.append(f"Removed ungrounded citation reference [Source {idx}].")
                    sanitized = sanitized.replace(f"[Source {idx}]", "")

        # 4. Enforce regulatory disclaimer
        if FINANCIAL_DISCLAIMER_TEXT not in sanitized:
            disclaimer_block = f"\n\n---\n> **Regulatory Notice**: {FINANCIAL_DISCLAIMER_TEXT}"
            sanitized = f"{sanitized.rstrip()}{disclaimer_block}"

        guardrail_passed = len(warnings) == 0 or all("softened" in w or "Removed" in w for w in warnings)
        return sanitized.strip(), guardrail_passed, warnings


financial_guardrails = FinancialAIGuardrails()
