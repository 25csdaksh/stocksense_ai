"""
MarketMind AI — Fundamentals Data Collector & Batch Ingestion Engine.
Phase 6.6: Continuous batch ingestion, error isolation, telemetry monitoring,
and data quality health reporting.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.fundamentals_service import fundamentals_service
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


DEFAULT_FUNDAMENTALS_UNIVERSE = [
    # Indian Benchmark Equities
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "ITC.NS",
    "SBIN.NS",
    "TATAMOTORS.NS",
    # US Benchmark Equities
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
]


class FundamentalsCollector:
    """Batch collector and quality telemetry tracker for corporate fundamentals."""

    def __init__(self, universe: Optional[List[str]] = None):
        self.universe: List[str] = universe or DEFAULT_FUNDAMENTALS_UNIVERSE
        self.records_processed: int = 0
        self.records_failed: int = 0
        self.duplicates_prevented: int = 0
        self.missing_fields_detected: int = 0
        self.last_successful_run: Optional[datetime] = None
        self.provider_status: Dict[str, str] = {
            "INDIAN_PROVIDER": "ONLINE",
            "US_PROVIDER": "ONLINE",
            "MOCK_PROVIDER": "ONLINE",
        }

    async def collect_single_symbol(
        self,
        symbol: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Collects, validates, caches, and persists fundamentals for a single symbol with error isolation."""
        try:
            norm = normalize_symbol(symbol)
            canonical = norm.canonical_symbol

            # 1. Fetch & cache profile
            profile = await fundamentals_service.get_company_profile(canonical)

            # 2. Fetch & cache overview + ratios
            overview = await fundamentals_service.get_overview(canonical)

            # 3. Fetch & cache multi-period statements
            await fundamentals_service.get_statements(canonical, "income", "annual")
            await fundamentals_service.get_statements(canonical, "balance_sheet", "annual")
            await fundamentals_service.get_statements(canonical, "cash_flow", "annual")

            # 4. Check for missing critical fields
            if overview and (overview.latest_income is None or overview.latest_balance is None):
                self.missing_fields_detected += 1

            # 5. Persist to database if active DB session is supplied
            if session:
                await fundamentals_service.persist_fundamentals(session, canonical, overview)

            self.records_processed += 1
            return {
                "symbol": canonical,
                "status": "SUCCESS",
                "data_source": overview.data_source.value if overview else "DEMO",
                "data_status": overview.data_status.value if overview else "DEMO",
            }
        except Exception as e:
            logger.error(f"FundamentalsCollector error for {symbol}: {e}")
            self.records_failed += 1
            return {
                "symbol": symbol,
                "status": "FAILED",
                "error": str(e),
            }

    async def collect_universe(
        self,
        symbols: Optional[List[str]] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Collects fundamentals across the entire configured universe."""
        target_symbols = symbols or self.universe
        results = []

        for sym in target_symbols:
            res = await self.collect_single_symbol(sym, session=session)
            results.append(res)
            # Yield control to event loop
            await asyncio.sleep(0.01)

        self.last_successful_run = datetime.utcnow()
        return {
            "total_symbols": len(target_symbols),
            "processed": len([r for r in results if r.get("status") == "SUCCESS"]),
            "failed": len([r for r in results if r.get("status") == "FAILED"]),
            "results": results,
            "timestamp": self.last_successful_run.isoformat(),
        }

    def get_health_report(self) -> Dict[str, Any]:
        """Returns health telemetry, record counts, and provider freshness."""
        now = datetime.utcnow()
        freshness = None
        if self.last_successful_run:
            freshness = int((now - self.last_successful_run).total_seconds())

        status_str = "HEALTHY"
        if self.records_failed > 0 and self.records_failed >= self.records_processed:
            status_str = "DEGRADED"

        return {
            "status": status_str,
            "provider_status": self.provider_status,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "duplicates_prevented": self.duplicates_prevented,
            "missing_fields_detected": self.missing_fields_detected,
            "last_successful_run": self.last_successful_run.isoformat() if self.last_successful_run else None,
            "freshness_seconds": freshness,
            "active_providers": ["INDIAN_PROVIDER", "US_PROVIDER", "MOCK_PROVIDER"],
        }


fundamentals_collector = FundamentalsCollector()
