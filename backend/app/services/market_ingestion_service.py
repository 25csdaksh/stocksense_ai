"""
MarketMind AI — TimescaleDB & PostgreSQL Market Data Ingestion Service.
Phase 6.1: High-throughput validated ingestion of OHLCV bars, quotes, and market indices into database models.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.stock import Stock, StockOHLCV, MarketIndex
from app.db.models.company import Company, Sector
from app.db.repositories.market_data_repository import MarketDataRepository
from app.db.repositories.stock_repository import StockRepository
from app.providers.market_data.models import (
    NormalizedQuote,
    HistoricalCandle,
    MarketIndexQuote
)
from app.providers.market_data.validator import validator
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class MarketIngestionService:
    """Ingestion service for time-series hypertable and index benchmarks."""

    @classmethod
    async def ingest_ohlcv_bars(
        cls,
        session: AsyncSession,
        symbol: str,
        bars: List[Union[Dict[str, Any], HistoricalCandle]],
        interval: str = "1d"
    ) -> int:
        """
        Validates OHLCV bars, resolves/creates the parent Stock record, and inserts batch records into StockOHLCV.
        """
        if not bars:
            return 0

        norm = normalize_symbol(symbol)
        canonical = norm.canonical_symbol

        # 1. Validate all candlestick records
        validated_candles = validator.filter_and_validate_candles(bars, symbol=canonical)
        if not validated_candles:
            logger.warning(f"No valid candles remaining after validation for {canonical}.")
            return 0

        # 2. Lookup or ensure parent Stock record
        stmt = select(Stock).where(Stock.ticker == canonical)
        res = await session.execute(stmt)
        stock_obj = res.scalar_one_or_none()

        if not stock_obj:
            # Check or create parent company
            comp_stmt = select(Company).where(Company.ticker == canonical)
            comp_res = await session.execute(comp_stmt)
            comp_obj = comp_res.scalar_one_or_none()

            if not comp_obj:
                sec_stmt = select(Sector).limit(1)
                sec_res = await session.execute(sec_stmt)
                sec_obj = sec_res.scalar_one_or_none()
                if not sec_obj:
                    sec_obj = Sector(
                        name="General Equities Sector",
                        code="GEN_EQ",
                        description="General Market Equities"
                    )
                    session.add(sec_obj)
                    await session.flush()

                comp_obj = Company(
                    name=norm.name or norm.display_symbol,
                    ticker=canonical,
                    sector_id=sec_obj.id,
                    country="IN" if norm.market == "IN" else "US"
                )
                session.add(comp_obj)
                await session.flush()

            stock_obj = Stock(
                company_id=comp_obj.id,
                ticker=canonical,
                exchange=norm.exchange,
                asset_class="EQUITY" if not norm.is_index else "INDEX",
                beta=1.0
            )
            session.add(stock_obj)
            await session.flush()

        # 3. Format batch records for hypertable insertion
        batch_records = []
        for candle in validated_candles:
            batch_records.append({
                "stock_id": stock_obj.id,
                "ticker": canonical,
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "adjusted_close": candle.adjusted_close,
                "volume": candle.volume,
                "interval": interval
            })

        repo = MarketDataRepository(session)
        inserted_count = await repo.insert_ohlcv_batch(batch_records)
        logger.info(f"Ingested {inserted_count} validated OHLCV bars for {canonical} into TimescaleDB.")
        return inserted_count

    @classmethod
    async def ingest_indices(
        cls,
        session: AsyncSession,
        indices: List[Union[Dict[str, Any], MarketIndexQuote]]
    ) -> int:
        """
        Upserts benchmark market indices into the market_indices table.
        """
        if not indices:
            return 0

        repo = MarketDataRepository(session)
        count = 0
        for idx in indices:
            if isinstance(idx, MarketIndexQuote):
                sym = idx.symbol
                name = idx.name
                price = idx.price
                change = idx.change
                change_pct = idx.change_pct
            else:
                sym = idx.get("symbol", "")
                name = idx.get("name", sym)
                price = float(idx.get("price", 0.0))
                change = float(idx.get("change", 0.0))
                change_pct = float(idx.get("change_pct", 0.0))

            if sym and price > 0:
                await repo.upsert_index(
                    symbol=sym,
                    name=name,
                    price=price,
                    change=change,
                    change_pct=change_pct
                )
                count += 1

        return count


market_ingestion_service = MarketIngestionService()
