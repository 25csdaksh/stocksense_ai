"""
MarketMind AI — Historical OHLCV Data Backfill & Incremental Ingestion Service.
Phase 6.3: Intelligent historical timeseries backfilling, incremental delta ingestion (latest_timestamp -> now),
gap detection, duplicate suppression, and TimescaleDB batch persistence.
"""
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.providers.market_data.models import (
    HistoricalCandle,
    HistoricalDataResponse,
    DataStatus
)
from app.providers.market_data.factory import provider_factory
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.providers.market_data.validator import validator
from app.providers.market_data.observability import log_market_data_operation
from app.services.market_quality_service import market_quality_service, MarketDataQualityReport
from app.services.market_ingestion_service import market_ingestion_service
from app.cache.market_cache import market_cache
from app.db.session import async_session_factory
from app.db.repositories.market_data_repository import MarketDataRepository


class BackfillResult(BaseModel):
    """Result summary of a historical backfill or incremental sync operation."""
    symbol: str
    timeframe: str = "6m"
    interval: str = "1d"
    is_incremental: bool = False
    last_timestamp_before: Optional[str] = None
    bars_fetched: int = 0
    bars_valid: int = 0
    bars_persisted: int = 0
    duplicates_filtered: int = 0
    gaps_detected: List[Dict[str, Any]] = Field(default_factory=list)
    quality_score: float = 100.0
    latency_ms: float = 0.0
    status: str = "SUCCESS"  # SUCCESS, PARTIAL, FAILED
    error_message: Optional[str] = None


class HistoricalDataBackfillService:
    """
    Manages historical backfilling and incremental timeseries ingestion into TimescaleDB.
    """

    @classmethod
    async def backfill_symbol_history(
        cls,
        symbol: str,
        timeframe: str = "6m",
        interval: str = "1d",
        force_full: bool = False
    ) -> BackfillResult:
        """
        Backfills or incrementally syncs historical OHLCV data for a given symbol.
        1. Checks TimescaleDB for existing latest bar timestamp.
        2. If records exist and not force_full -> Fetches only (latest_timestamp -> now).
        3. Deduplicates, validates, and batch inserts new bars.
        4. Evaluates data quality & gaps.
        5. Updates Redis cache.
        """
        start_t = time.time()
        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        result = BackfillResult(
            symbol=canonical,
            timeframe=timeframe,
            interval=interval
        )

        try:
            # 1. Determine latest bar in database for incremental sync
            latest_bar = None
            async with async_session_factory() as session:
                repo = MarketDataRepository(session)
                latest_bar = await repo.get_latest_bar(canonical)

            is_incremental = False
            start_date_str = None
            if latest_bar and not force_full and latest_bar.timestamp:
                is_incremental = True
                result.is_incremental = True
                result.last_timestamp_before = latest_bar.timestamp.isoformat()
                # Start from latest recorded bar
                start_date_str = latest_bar.timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # 2. Fetch data from resolved market provider
            provider = provider_factory.get_provider(symbol=canonical)
            hist_response = await provider.get_historical_data(
                symbol=canonical,
                start=start_date_str,
                interval=interval,
                timeframe=timeframe
            )

            raw_bars = hist_response.bars
            result.bars_fetched = len(raw_bars)

            if not raw_bars:
                result.status = "SUCCESS"
                result.latency_ms = round((time.time() - start_t) * 1000.0, 2)
                return result

            # 3. Filter and Validate Candlesticks
            valid_candles = validator.filter_and_validate_candles(raw_bars, symbol=canonical)
            result.bars_valid = len(valid_candles)

            # 4. Perform Quality Assessment & Gap Detection
            quality_report = market_quality_service.evaluate_timeseries_quality(
                symbol=canonical,
                candles=valid_candles,
                interval=interval,
                data_source=hist_response.data_source
            )
            result.gaps_detected = quality_report.gaps_detected
            result.duplicates_filtered = quality_report.duplicate_count
            result.quality_score = quality_report.quality_score

            # 5. Persist to TimescaleDB
            async with async_session_factory() as session:
                persisted_count = await market_ingestion_service.ingest_ohlcv_bars(
                    session=session,
                    symbol=canonical,
                    bars=valid_candles,
                    interval=interval
                )
                await session.commit()
                result.bars_persisted = persisted_count

            # 6. Update Redis Cache
            await market_cache.set_history(
                symbol=canonical,
                history_data=hist_response.model_dump(),
                timeframe=timeframe,
                interval=interval
            )

            result.status = "SUCCESS"
            elapsed_ms = (time.time() - start_t) * 1000.0
            result.latency_ms = round(elapsed_ms, 2)

            log_market_data_operation(
                provider="HistoricalDataBackfillService",
                operation=f"backfill[{'INCREMENTAL' if is_incremental else 'FULL'}]",
                symbol=canonical,
                latency_ms=elapsed_ms,
                success=True
            )
            return result

        except Exception as exc:
            elapsed_ms = (time.time() - start_t) * 1000.0
            result.latency_ms = round(elapsed_ms, 2)
            result.status = "FAILED"
            result.error_message = str(exc)
            logger.warning(f"Backfill error for '{canonical}': {exc}")
            return result

    @classmethod
    async def backfill_universe_history(
        cls,
        symbols: Optional[List[str]] = None,
        timeframe: str = "6m",
        interval: str = "1d",
        force_full: bool = False
    ) -> Dict[str, BackfillResult]:
        """
        Runs batch backfill across multiple symbols with failure isolation.
        """
        from app.services.market_data_collector import market_data_collector
        target_symbols = symbols or market_data_collector.get_monitored_universe()["equities"]
        results: Dict[str, BackfillResult] = {}

        for sym in target_symbols:
            res = await cls.backfill_symbol_history(
                symbol=sym,
                timeframe=timeframe,
                interval=interval,
                force_full=force_full
            )
            results[sym] = res

        return results


market_backfill_service = HistoricalDataBackfillService()
