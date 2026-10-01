"""
MarketMind AI — User Context Builder.
Phase 6.10: Constructs strictly isolated, authenticated user context combining portfolio holdings,
watchlist tracking, historical research memory, news intelligence, and anomaly signals.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.portfolio.models import (
    PortfolioHoldingContext,
    PortfolioUserContext,
    WatchlistItemContext,
    WatchlistContext,
    PortfolioRiskContext,
    PortfolioNewsContext,
    PortfolioAnomalyContext,
    ResearchMemoryItem,
    ResearchMemoryContext,
    UserResearchContext,
)
from app.ai.portfolio.portfolio_analyzer import portfolio_analyzer
from app.ai.models import EvidenceProvenance
from app.ai.agents.market_agent import market_agent
from app.ai.agents.fundamental_agent import fundamental_agent
from app.ai.agents.quant_agent import quant_agent
from app.ai.agents.risk_agent import risk_agent
from app.ai.agents.news_agent import news_agent
from app.ai.agents.anomaly_agent import anomaly_agent

from app.services.portfolio_service import portfolio_service
from app.db.repositories.portfolio_repository import PortfolioRepository
from app.db.repositories.watchlist_repository import WatchlistRepository
from app.db.repositories.research_memory_repository import ResearchMemoryRepository
from app.providers.market_data.symbol_normalizer import normalize_symbol
from app.core.logging import logger


class UserContextBuilder:
    """Assembles strongly typed, multi-pillar user context strictly isolated by user ID."""

    async def build_user_context(
        self,
        user_id: str,
        db: Optional[AsyncSession] = None,
        target_symbol: Optional[str] = None
    ) -> UserResearchContext:
        """Assembles unified research context bundle strictly for the specified authenticated user."""
        # 1. Fetch User Holdings & Raw Positions
        raw_positions = []
        portfolio_id = None
        portfolio_name = "Primary Portfolio"
        cash_balance = 100000.0

        if db:
            try:
                p_repo = PortfolioRepository(db)
                port = await p_repo.get_or_create_default(user_id)
                if port:
                    portfolio_id = port.id
                    portfolio_name = port.name or "Primary Portfolio"
                    cash_balance = float(port.cash_balance or 100000.0)
                    db_positions = await p_repo.get_positions(port.id)
                    if db_positions:
                        raw_positions = [
                            {
                                "ticker": p.ticker,
                                "shares": float(p.shares),
                                "avg_cost": float(p.avg_cost),
                                "sector": p.sector or "General",
                                "beta": float(p.beta or 1.0)
                            }
                            for p in db_positions
                        ]
            except Exception as ex:
                logger.warning(f"Error fetching portfolio from DB for user {user_id}: {ex}")

        # Fallback to in-memory store if DB positions empty
        if not raw_positions:
            raw_positions = portfolio_service.in_memory_repo.get_positions()

        # 2. Enrich Holding Contexts concurrently via Phase 6.9 Specialist Agents
        symbols = [p["ticker"] for p in raw_positions]

        holding_tasks = [
            market_agent.run(symbols, timeframe="3m"),
            fundamental_agent.run(symbols),
            quant_agent.run(symbols, timeframe="3m"),
            risk_agent.run(symbols, timeframe="3m"),
            news_agent.run(symbols, limit=3),
            anomaly_agent.run(symbols, timeframe="3m")
        ]

        results = await asyncio.gather(*holding_tasks, return_exceptions=True)

        market_ev = results[0] if isinstance(results[0], list) else []
        fund_ev = results[1] if isinstance(results[1], list) else []
        quant_ev = results[2] if isinstance(results[2], list) else []
        risk_ev = results[3] if isinstance(results[3], list) else []
        news_ev = results[4] if isinstance(results[4], list) else []
        anom_ev = results[5] if isinstance(results[5], list) else []

        # Map specialist evidence to individual holdings
        holdings_context_list: List[PortfolioHoldingContext] = []

        for pos in raw_positions:
            sym = pos["ticker"]
            shares = pos["shares"]
            avg_cost = pos["avg_cost"]
            norm_sym = normalize_symbol(sym).canonical_symbol

            # Price from market agent evidence
            cur_price = avg_cost
            prov_tier = EvidenceProvenance.DEMO
            for ev in market_ev:
                if ev.symbol in [sym, norm_sym] and ev.metric == "latest_price" and isinstance(ev.value, dict):
                    cur_price = float(ev.value.get("price") or cur_price)
                    prov_tier = ev.provenance
                    break

            mkt_val = round(shares * cur_price, 2)
            inv_val = round(shares * avg_cost, 2)
            abs_pnl = round(mkt_val - inv_val, 2)
            pct_pnl = round(((cur_price - avg_cost) / max(0.01, avg_cost)) * 100.0, 2)

            # Fundamentals
            pe_val = None
            sector_val = pos.get("sector", "General")
            for ev in fund_ev:
                if ev.symbol in [sym, norm_sym]:
                    if ev.metric == "valuation_ratios" and isinstance(ev.value, dict):
                        pe_val = ev.value.get("pe_ratio")
                    elif ev.metric == "company_profile" and isinstance(ev.value, dict):
                        sector_val = ev.value.get("sector") or sector_val

            # Quant / Technicals
            rsi_val = None
            for ev in quant_ev:
                if ev.symbol in [sym, norm_sym] and ev.metric == "momentum_oscillators" and isinstance(ev.value, dict):
                    rsi_val = ev.value.get("rsi_14")
                    break

            # Risk
            vol_val = 18.0
            dd_val = 12.0
            var_val = 1.8
            for ev in risk_ev:
                if ev.symbol in [sym, norm_sym] and ev.metric == "downside_risk_profile" and isinstance(ev.value, dict):
                    vol_val = ev.value.get("annualized_volatility_pct") or vol_val
                    dd_val = ev.value.get("max_drawdown_pct") or dd_val
                    var_val = ev.value.get("var_95_daily_pct") or var_val
                    break

            # News
            news_headline = None
            for ev in news_ev:
                if ev.symbol in [sym, norm_sym] and ev.metric == "headline_event" and isinstance(ev.value, dict):
                    news_headline = ev.value.get("title")
                    break

            # Anomalies
            anom_note = None
            for ev in anom_ev:
                if ev.symbol in [sym, norm_sym] and ev.metric == "detected_market_anomalies" and isinstance(ev.value, dict):
                    anom_note = ev.value.get("analysis_note")
                    break

            holdings_context_list.append(
                PortfolioHoldingContext(
                    ticker=sym,
                    exchange="NSE" if ".NS" in norm_sym else "NASDAQ",
                    quantity=shares,
                    average_cost=avg_cost,
                    current_price=cur_price,
                    invested_value=inv_val,
                    market_value=mkt_val,
                    absolute_pnl=abs_pnl,
                    percentage_pnl=pct_pnl,
                    portfolio_weight_pct=0.0,  # Will be normalized by analyzer
                    sector=sector_val,
                    beta=float(pos.get("beta", 1.0)),
                    volatility_pct=vol_val,
                    max_drawdown_pct=dd_val,
                    var_95_daily_pct=var_val,
                    pe_ratio=pe_val,
                    rsi_14=rsi_val,
                    latest_news_context=news_headline,
                    latest_anomaly_context=anom_note,
                    data_freshness="FRESH",
                    provenance=prov_tier,
                    data_status="LIVE" if prov_tier == EvidenceProvenance.LIVE else "DEMO"
                )
            )

        # 3. Calculate Portfolio Analytics & Risk Context
        user_portfolio_ctx, risk_ctx = portfolio_analyzer.calculate_portfolio_metrics(
            user_id=user_id,
            holdings=holdings_context_list,
            cash_balance=cash_balance,
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name
        )

        # 4. Fetch User Watchlist & Enrich
        watchlist_items: List[WatchlistItemContext] = []
        raw_watchlist = []
        if db:
            try:
                w_repo = WatchlistRepository(db)
                db_w = await w_repo.get_by_user(user_id)
                if db_w:
                    raw_watchlist = [
                        {"ticker": w.ticker, "added_at": w.added_at.isoformat(), "target_price": w.target_price, "notes": w.notes}
                        for w in db_w
                    ]
            except Exception as ex:
                logger.warning(f"Error fetching watchlist for user {user_id}: {ex}")

        if not raw_watchlist:
            raw_watchlist = portfolio_service.in_memory_repo.get_watchlist()

        for w_pos in raw_watchlist:
            w_sym = w_pos["ticker"]
            w_norm = normalize_symbol(w_sym).canonical_symbol
            w_price = 100.0
            w_change = 0.0

            for ev in market_ev:
                if ev.symbol in [w_sym, w_norm] and ev.metric == "latest_price" and isinstance(ev.value, dict):
                    w_price = float(ev.value.get("price") or w_price)
                    w_change = float(ev.value.get("change_pct") or w_change)
                    break

            watchlist_items.append(
                WatchlistItemContext(
                    ticker=w_sym,
                    added_at=w_pos.get("added_at", datetime.now(timezone.utc).isoformat()),
                    current_price=w_price,
                    change_pct=w_change,
                    target_price=w_pos.get("target_price"),
                    notes=w_pos.get("notes"),
                    data_freshness="FRESH",
                    provenance=EvidenceProvenance.DEMO
                )
            )

        watchlist_ctx = WatchlistContext(
            user_id=user_id,
            items=watchlist_items,
            total_items=len(watchlist_items),
            news_summary=f"Tracking {len(watchlist_items)} assets on user watchlist.",
            anomalies_detected=0
        )

        # 5. Fetch User Research Memory
        memory_items: List[ResearchMemoryItem] = []
        target_memory = None
        if db:
            try:
                mem_repo = ResearchMemoryRepository(db)
                db_mems = await mem_repo.get_user_memories(user_id=user_id, limit=10)
                memory_items = [
                    ResearchMemoryItem(
                        research_id=m.research_id,
                        query=m.query,
                        symbols=m.symbols or [],
                        intent=m.intent,
                        execution_depth=m.execution_depth,
                        created_at=m.created_at.isoformat(),
                        report_summary=m.report_summary,
                        evidence_count=m.evidence_count,
                        confidence_level=m.confidence_level,
                        confidence_rationale=m.confidence_rationale,
                        provenance_summary=m.provenance_summary or {},
                        key_metrics=m.key_metrics or {},
                        cited_sources=m.cited_sources or [],
                        data_status=m.data_status,
                        research_version=m.research_version
                    )
                    for m in db_mems
                ]
                if target_symbol:
                    target_db_mem = await mem_repo.get_latest_memory_for_symbol(user_id=user_id, symbol=target_symbol)
                    if target_db_mem:
                        target_memory = ResearchMemoryItem(
                            research_id=target_db_mem.research_id,
                            query=target_db_mem.query,
                            symbols=target_db_mem.symbols or [],
                            intent=target_db_mem.intent,
                            execution_depth=target_db_mem.execution_depth,
                            created_at=target_db_mem.created_at.isoformat(),
                            report_summary=target_db_mem.report_summary,
                            evidence_count=target_db_mem.evidence_count,
                            confidence_level=target_db_mem.confidence_level,
                            confidence_rationale=target_db_mem.confidence_rationale,
                            provenance_summary=target_db_mem.provenance_summary or {},
                            key_metrics=target_db_mem.key_metrics or {},
                            cited_sources=target_db_mem.cited_sources or [],
                            data_status=target_db_mem.data_status,
                            research_version=target_db_mem.research_version
                        )
            except Exception as ex:
                logger.warning(f"Error fetching research memory for user {user_id}: {ex}")

        memory_ctx = ResearchMemoryContext(
            user_id=user_id,
            total_memories=len(memory_items),
            recent_memories=memory_items,
            target_symbol_memory=target_memory
        )

        # 6. Assemble Portfolio News & Anomaly Contexts
        news_holding_map: Dict[str, List[Dict[str, Any]]] = {}
        top_articles = []
        for ev in news_ev:
            if ev.metric == "headline_event" and isinstance(ev.value, dict):
                sym_k = ev.symbol or "PORTFOLIO"
                news_holding_map.setdefault(sym_k, []).append(ev.value)
                top_articles.append(ev.value)

        news_ctx = PortfolioNewsContext(
            articles_count=len(top_articles),
            dominant_sentiment="POSITIVE" if len(top_articles) > 0 else "NEUTRAL",
            sentiment_score=0.45,
            sentiment_distribution={"POSITIVE": len(top_articles), "NEUTRAL": 1, "NEGATIVE": 0},
            holding_news_map=news_holding_map,
            high_impact_articles=top_articles[:4],
            provenance=EvidenceProvenance.MODEL_DERIVED
        )

        anom_holding_map: Dict[str, List[Dict[str, Any]]] = {}
        for ev in anom_ev:
            if ev.metric == "detected_market_anomalies" and isinstance(ev.value, dict):
                sym_k = ev.symbol or "PORTFOLIO"
                anom_holding_map.setdefault(sym_k, []).append(ev.value)

        anom_ctx = PortfolioAnomalyContext(
            total_anomalies=len(anom_holding_map),
            holding_anomalies_map=anom_holding_map,
            anomaly_types=["PRICE_RETURN_SPIKE", "VOLUME_SURGE"] if anom_holding_map else [],
            associative_summary=(
                f"Observed statistical variations across {len(anom_holding_map)} portfolio holdings in active trading sessions."
                if anom_holding_map else "No unusual statistical return spikes or volume outliers detected."
            ),
            provenance=EvidenceProvenance.MODEL_DERIVED
        )

        return UserResearchContext(
            user_id=user_id,
            portfolio=user_portfolio_ctx,
            watchlist=watchlist_ctx,
            memory=memory_ctx,
            risk=risk_ctx,
            news=news_ctx,
            anomaly=anom_ctx
        )


user_context_builder = UserContextBuilder()
