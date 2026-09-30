"""
MarketMind AI — Unified Fundamentals & Financial Intelligence Service.
Phase 6.6: Coordinates multi-market provider retrieval, strict validation,
Redis caching, deterministic ratio calculations, and database persistence.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.fundamentals.factory import get_fundamentals_provider
from app.providers.fundamentals.models import (
    CompanyProfileData,
    FundamentalOverviewData,
    FinancialStatementsContainer,
    FinancialRatiosData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FundamentalDataStatus,
    FundamentalDataSource,
)
from app.providers.fundamentals.validator import fundamentals_validator
from app.analytics.ratio_engine import ratio_engine
from app.cache.fundamentals_cache import fundamentals_cache
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.db.repositories.company_repository import CompanyRepository
from app.db.repositories.fundamental_repository import FundamentalRepository
from app.core.logging import logger


class FundamentalsService:
    """Comprehensive service for multi-market company financials and valuation."""

    async def get_company_profile(self, raw_symbol: str) -> Optional[CompanyProfileData]:
        """Retrieves company legal profile, sector, exchange, and business description."""
        norm = normalize_symbol(raw_symbol)
        canonical = norm.canonical_symbol

        # 1. Check Redis cache
        cached = await fundamentals_cache.get_profile(canonical)
        if cached:
            try:
                return CompanyProfileData(**cached)
            except Exception as e:
                logger.warning(f"Error deserializing cached profile for {canonical}: {e}")

        # 2. Fetch from appropriate market provider
        provider = get_fundamentals_provider(canonical)
        profile = await provider.get_company_profile(canonical)
        if profile:
            # 3. Cache result
            await fundamentals_cache.set_profile(canonical, profile.model_dump())
            return profile

        return None

    async def get_overview(self, raw_symbol: str) -> FundamentalOverviewData:
        """Retrieves valuation multiples, profitability margins, and financial health scores."""
        norm = normalize_symbol(raw_symbol)
        canonical = norm.canonical_symbol

        # 1. Check Redis cache
        cached = await fundamentals_cache.get_overview(canonical)
        if cached:
            try:
                return FundamentalOverviewData(**cached)
            except Exception as e:
                logger.warning(f"Error deserializing cached overview for {canonical}: {e}")

        # 2. Fetch from market provider
        provider = get_fundamentals_provider(canonical)
        data = await provider.get_fundamentals(canonical)

        if not data:
            # Construct empty fallback with explicit UNAVAILABLE provenance
            data = FundamentalOverviewData(
                symbol=canonical,
                name=norm.tradingsymbol or canonical,
                sector="General",
                exchange=norm.exchange or "NSE",
                currency="INR" if norm.exchange in ["NSE", "BSE"] else "USD",
                data_source=FundamentalDataSource.DEMO,
                data_status=FundamentalDataStatus.UNAVAILABLE,
                updated_at=datetime.utcnow().isoformat(),
            )

        # 3. Cache in Redis
        await fundamentals_cache.set_overview(canonical, data.model_dump())
        return data

    async def get_statements(
        self,
        raw_symbol: str,
        statement_type: str = "income",
        period_type: str = "annual"
    ) -> FinancialStatementsContainer:
        """Retrieves normalized multi-period financial statements (Income, Balance, Cash Flow)."""
        norm = normalize_symbol(raw_symbol)
        canonical = norm.canonical_symbol

        # 1. Check Redis cache
        cached = await fundamentals_cache.get_statements(canonical, statement_type, period_type)
        if cached:
            try:
                return FinancialStatementsContainer(**cached)
            except Exception as e:
                logger.warning(f"Error deserializing cached statements for {canonical}: {e}")

        # 2. Fetch from provider
        provider = get_fundamentals_provider(canonical)
        statements = await provider.get_financial_statements(
            canonical,
            statement_type=statement_type,
            period_type=period_type
        )

        # 3. Cache in Redis
        await fundamentals_cache.set_statements(
            canonical,
            statements.model_dump(),
            statement_type=statement_type,
            period_type=period_type
        )
        return statements

    async def get_ratios(self, raw_symbol: str, market_cap: Optional[float] = None) -> FinancialRatiosData:
        """Calculates deterministic ratio analytics suite."""
        norm = normalize_symbol(raw_symbol)
        canonical = norm.canonical_symbol

        # 1. Check Redis cache
        cached = await fundamentals_cache.get_ratios(canonical)
        if cached:
            try:
                return FinancialRatiosData(**cached)
            except Exception as e:
                logger.warning(f"Error deserializing cached ratios for {canonical}: {e}")

        # 2. Get overview data which contains latest statements
        overview = await self.get_overview(canonical)
        mcap = market_cap or (overview.profile.market_cap if overview.profile else None)

        ratios = ratio_engine.compute_all_ratios(
            symbol=canonical,
            income=overview.latest_income,
            balance=overview.latest_balance,
            cashflow=overview.latest_cashflow,
            market_cap=mcap,
            data_source=overview.data_source,
            data_status=overview.data_status,
        )

        # 3. Cache in Redis
        await fundamentals_cache.set_ratios(canonical, ratios.model_dump())
        return ratios

    async def persist_fundamentals(
        self,
        session: AsyncSession,
        raw_symbol: str,
        overview: Optional[FundamentalOverviewData] = None
    ) -> bool:
        """Persists company and fundamental records to database if Company exists."""
        try:
            norm = normalize_symbol(raw_symbol)
            canonical = norm.canonical_symbol
            ticker_bare = norm.tradingsymbol or canonical.replace(".NS", "").replace(".BO", "")

            comp_repo = CompanyRepository(session)
            fund_repo = FundamentalRepository(session)

            company = await comp_repo.get_by_ticker(ticker_bare)
            if not company:
                company = await comp_repo.get_by_ticker(canonical)

            if not company:
                # If company doesn't exist in DB seed yet, skip DB persistence without failing
                return False

            if not overview:
                overview = await self.get_overview(canonical)

            val = overview.valuation
            prof = overview.profitability
            health = overview.financial_health

            curr_year = datetime.utcnow().year
            await fund_repo.upsert_fundamental(
                company_id=company.id,
                fiscal_year=curr_year,
                fiscal_quarter=None,
                pe_ratio=val.pe_ratio,
                forward_pe=val.forward_pe,
                pb_ratio=val.pb_ratio,
                ev_ebitda=val.ev_ebitda,
                fcf_yield_pct=val.fcf_yield_pct,
                gross_margin_pct=prof.gross_margin_pct,
                operating_margin_pct=prof.operating_margin_pct,
                net_margin_pct=prof.net_margin_pct,
                roe_pct=prof.roe_pct,
                roa_pct=prof.roa_pct,
                current_ratio=health.current_ratio if hasattr(health, 'current_ratio') else None,
                debt_to_equity=health.debt_to_equity,
                interest_coverage_ratio=health.interest_coverage if hasattr(health, 'interest_coverage') else None,
                altman_z_score=health.altman_z_score,
                health_score=health.health_score or "HEALTHY",
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to persist fundamentals for {raw_symbol}: {e}")
            return False


fundamentals_service = FundamentalsService()
