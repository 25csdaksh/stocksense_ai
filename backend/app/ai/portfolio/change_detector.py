"""
MarketMind AI — Portfolio & Research Change Detection Engine.
Phase 6.10: Deterministic change auditing comparing historical research memory
and prior baseline snapshots against current verified multi-pillar market telemetry.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.ai.portfolio.models import (
    PortfolioUserContext,
    ResearchMemoryItem,
    PortfolioChangeItem,
    PortfolioChangeReport,
    PortfolioHoldingContext,
)


class PortfolioChangeDetector:
    """Detects factual deltas between historical research records and current market state."""

    @classmethod
    def compare_memory_vs_current(
        cls,
        memory: ResearchMemoryItem,
        current_holdings: List[PortfolioHoldingContext],
        current_portfolio: PortfolioUserContext,
    ) -> PortfolioChangeReport:
        """Compares historical research key metrics against current live/demo verified telemetry."""
        changes: List[PortfolioChangeItem] = []
        holding_changes: List[PortfolioChangeItem] = []
        risk_changes: List[PortfolioChangeItem] = []
        val_changes: List[PortfolioChangeItem] = []
        res_changes: List[PortfolioChangeItem] = []

        prev_metrics = memory.key_metrics or {}
        prev_date = memory.created_at

        # 1. Compare target symbols in memory
        for sym in memory.symbols:
            # Find in current holdings
            holding = next((h for h in current_holdings if h.ticker.upper() == sym.upper() or sym.upper() in h.ticker.upper()), None)
            if holding:
                # Check price change if previous price was stored
                prev_price = prev_metrics.get(f"{sym}_price") or prev_metrics.get("price")
                if prev_price is not None and isinstance(prev_price, (int, float)):
                    cur_p = holding.current_price
                    diff = round(cur_p - float(prev_price), 2)
                    diff_pct = round((diff / max(0.01, float(prev_price))) * 100.0, 2)
                    if abs(diff_pct) >= 0.5:
                        c_item = PortfolioChangeItem(
                            metric="price",
                            symbol=sym,
                            previous_value=prev_price,
                            current_value=cur_p,
                            absolute_change=diff,
                            percentage_change=diff_pct,
                            description=f"{sym} price shifted from {prev_price} to {cur_p} ({'+' if diff > 0 else ''}{diff_pct}%) since previous research on {prev_date[:10]}.",
                            previous_date=prev_date,
                            change_type="PRICE_SHIFT"
                        )
                        changes.append(c_item)
                        holding_changes.append(c_item)

                # Check P/E valuation change
                prev_pe = prev_metrics.get(f"{sym}_pe") or prev_metrics.get("pe_ratio")
                if prev_pe is not None and holding.pe_ratio is not None:
                    pe_diff = round(holding.pe_ratio - float(prev_pe), 2)
                    if abs(pe_diff) >= 0.5:
                        c_item = PortfolioChangeItem(
                            metric="pe_ratio",
                            symbol=sym,
                            previous_value=prev_pe,
                            current_value=holding.pe_ratio,
                            absolute_change=pe_diff,
                            percentage_change=round((pe_diff / max(0.01, float(prev_pe))) * 100.0, 2),
                            description=f"{sym} P/E valuation multiple moved from {prev_pe} to {holding.pe_ratio}.",
                            previous_date=prev_date,
                            change_type="VALUATION_CHANGE"
                        )
                        changes.append(c_item)
                        val_changes.append(c_item)

                # Check Volatility change
                prev_vol = prev_metrics.get(f"{sym}_volatility") or prev_metrics.get("volatility_pct")
                if prev_vol is not None and holding.volatility_pct is not None:
                    vol_diff = round(holding.volatility_pct - float(prev_vol), 2)
                    if abs(vol_diff) >= 1.0:
                        c_item = PortfolioChangeItem(
                            metric="volatility_pct",
                            symbol=sym,
                            previous_value=prev_vol,
                            current_value=holding.volatility_pct,
                            absolute_change=vol_diff,
                            percentage_change=round((vol_diff / max(0.01, float(prev_vol))) * 100.0, 2),
                            description=f"{sym} annualized volatility moved from {prev_vol}% to {holding.volatility_pct}%.",
                            previous_date=prev_date,
                            change_type="RISK_SHIFT"
                        )
                        changes.append(c_item)
                        risk_changes.append(c_item)

        # 2. General Research Confidence change
        prev_conf = memory.confidence_level
        cur_conf = current_portfolio.data_status
        c_item = PortfolioChangeItem(
            metric="research_freshness",
            symbol="PORTFOLIO",
            previous_value=f"Snapshot from {prev_date[:10]} (Confidence: {prev_conf})",
            current_value=f"Active verified session (Status: {cur_conf})",
            description=f"Current verification session contains newer market observations than prior research ({prev_date[:10]}).",
            previous_date=prev_date,
            change_type="METRIC_UPDATE"
        )
        changes.append(c_item)
        res_changes.append(c_item)

        summary_text = (
            f"Identified {len(changes)} factual metric updates relative to prior research on {prev_date[:10]}."
            if changes else "No material metric discrepancies observed relative to historical research baseline."
        )

        return PortfolioChangeReport(
            total_changes=len(changes),
            holding_changes=holding_changes,
            risk_changes=risk_changes,
            valuation_changes=val_changes,
            research_changes=res_changes,
            summary=summary_text
        )

    @classmethod
    def detect_portfolio_internal_changes(
        cls,
        holdings: List[PortfolioHoldingContext],
        portfolio: PortfolioUserContext,
    ) -> PortfolioChangeReport:
        """Audits current portfolio allocations for notable concentration or weighting shifts."""
        changes: List[PortfolioChangeItem] = []
        holding_changes: List[PortfolioChangeItem] = []
        risk_changes: List[PortfolioChangeItem] = []

        for h in holdings:
            if h.portfolio_weight_pct > 25.0:
                c_item = PortfolioChangeItem(
                    metric="portfolio_weight_pct",
                    symbol=h.ticker,
                    previous_value="25.0% Benchmark Threshold",
                    current_value=f"{h.portfolio_weight_pct}%",
                    percentage_change=h.portfolio_weight_pct,
                    description=f"{h.ticker} portfolio market weight ({h.portfolio_weight_pct}%) exceeds single-position threshold (25%).",
                    change_type="WEIGHT_SHIFT"
                )
                changes.append(c_item)
                holding_changes.append(c_item)

            if (h.volatility_pct or 0) > 30.0:
                c_item = PortfolioChangeItem(
                    metric="volatility_pct",
                    symbol=h.ticker,
                    previous_value="30.0% Elevated Vol Threshold",
                    current_value=f"{h.volatility_pct}%",
                    percentage_change=h.volatility_pct,
                    description=f"{h.ticker} displays elevated annualized volatility ({h.volatility_pct}%).",
                    change_type="RISK_SHIFT"
                )
                changes.append(c_item)
                risk_changes.append(c_item)

        summary_text = (
            f"Surfaced {len(changes)} factual exposure and volatility observations across portfolio assets."
            if changes else "Portfolio weights and asset volatility remain within standard operational bands."
        )

        return PortfolioChangeReport(
            total_changes=len(changes),
            holding_changes=holding_changes,
            risk_changes=risk_changes,
            valuation_changes=[],
            research_changes=[],
            summary=summary_text
        )


change_detector = PortfolioChangeDetector()
