"""
MarketMind AI — Operational Failure Logger & Alerting Evaluator.
Phase 6.8: Centralized sanitized audit logging of runtime anomalies, provider failures,
validation rejections, and SLA breaches. Automatically redacts all credentials and secrets.
"""
import re
import uuid
import collections
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.observability.models import (
    OperationalFailureRecord,
    ErrorCategory,
    AlertSeverity,
)


class OperationalFailureLogger:
    """Ring-buffer storage for operational failure events with secret sanitization."""

    # Secret and credential regex matchers for sanitization
    REDACTION_PATTERNS = [
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\'])([^"\']+)["\']', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(password["\']?\s*[:=]\s*["\'])([^"\']+)["\']', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(secret["\']?\s*[:=]\s*["\'])([^"\']+)["\']', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(bearer\s+)([a-zA-Z0-9_\-\.]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(postgres(?:ql)?://)([^:@/]+):([^@/]+)@', re.IGNORECASE), r'\1\2:[REDACTED]@'),
        (re.compile(r'(redis://)([^:@/]+):([^@/]+)@', re.IGNORECASE), r'\1\2:[REDACTED]@'),
    ]

    def __init__(self, max_records: int = 500):
        self._records = collections.deque(maxlen=max_records)

    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """Strips credentials, auth headers, and sensitive strings from log messages."""
        if not message:
            return ""
        sanitized = message
        for pattern, replacement in cls.REDACTION_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def log_failure(
        self,
        component: str,
        provider: Optional[str] = None,
        symbol: Optional[str] = None,
        error_type: ErrorCategory = ErrorCategory.UNKNOWN_ERROR,
        severity: AlertSeverity = AlertSeverity.WARNING,
        message: str = ""
    ) -> OperationalFailureRecord:
        """Records a sanitized operational failure."""
        record = OperationalFailureRecord(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            component=component,
            provider=provider,
            symbol=symbol,
            error_type=error_type,
            severity=severity,
            message=self.sanitize_message(message)
        )
        self._records.appendleft(record)
        return record

    def get_recent_failures(
        self,
        limit: int = 50,
        severity: Optional[AlertSeverity] = None,
        component: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[OperationalFailureRecord]:
        """Retrieves recent failure records matching optional filter criteria."""
        results = []
        for r in self._records:
            if severity and r.severity != severity:
                continue
            if component and r.component.lower() != component.lower():
                continue
            if symbol and (not r.symbol or r.symbol.upper() != symbol.upper()):
                continue
            results.append(r)
            if len(results) >= limit:
                break
        return results

    def clear(self) -> None:
        """Clears all in-memory records (useful for test isolation)."""
        self._records.clear()


failure_logger = OperationalFailureLogger()
