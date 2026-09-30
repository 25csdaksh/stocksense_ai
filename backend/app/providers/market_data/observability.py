"""
MarketMind AI — Market Data Observability & Safe Structured Telemetry.
Ensures zero credentials, secrets, tokens, or passwords ever leak into application logs or telemetry spans.
"""
import time
import re
from typing import Dict, Any, Optional
from app.core.logging import logger

# Regex patterns to sanitize sensitive tokens
SENSITIVE_KEY_PATTERNS = [
    r"api[_-]?key",
    r"secret",
    r"token",
    r"password",
    r"totp",
    r"authorization",
    r"jwt",
    r"client[_-]?secret"
]


def sanitize_sensitive_data(data: Any) -> Any:
    """Recursively redacts values for any dictionary key matching sensitive authentication patterns."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(re.search(pat, k_lower) for pat in SENSITIVE_KEY_PATTERNS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_sensitive_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_sensitive_data(item) for item in data]
    return data


def log_market_data_operation(
    provider: str,
    operation: str,
    symbol: Optional[str] = None,
    latency_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """Logs structured telemetry for provider invocations without exposing credentials."""
    safe_extra = sanitize_sensitive_data(extra or {})
    log_payload = {
        "event": "market_data_provider_call",
        "provider": provider,
        "operation": operation,
        "symbol": symbol,
        "latency_ms": round(latency_ms, 2) if latency_ms is not None else None,
        "success": success,
        "error": error,
        **safe_extra
    }

    if success:
        logger.info(
            f"MarketDataProvider [{provider}] op={operation} sym={symbol or 'ALL'} "
            f"latency={log_payload['latency_ms']}ms status=SUCCESS"
        )
    else:
        logger.warning(
            f"MarketDataProvider [{provider}] op={operation} sym={symbol or 'ALL'} "
            f"status=FAILED error={error}"
        )
