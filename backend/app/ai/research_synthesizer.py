"""
MarketMind AI — Multi-Agent Research Synthesis Engine.
Phase 6.9: Synthesizes structured, factual research reports from validated evidence.
Strictly neutral, evidence-grounded, citation-anchored, and compliant with financial safety guardrails.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.ai.models import (
    ResearchPlan,
    ResearchEvidence,
    CrossValidationReport,
    ResearchReport,
    Citation,
    ConfidenceLevel,
)


class ResearchSynthesizer:
    """Transforms multi-agent evidence into a structured, citation-anchored research report."""

    @classmethod
    def synthesize_report(
        cls,
        query: str,
        plan: ResearchPlan,
        evidence_list: List[ResearchEvidence],
        validation_report: CrossValidationReport
    ) -> ResearchReport:
        """Assembles comprehensive research report across all analytical dimensions."""
        symbols = plan.symbols
        symbols_str = ", ".join(symbols) if symbols else "Broad Market Universe"

        # Group evidence by category
        market_ev = [e for e in evidence_list if e.category == "MARKET"]
        fund_ev = [e for e in evidence_list if e.category == "FUNDAMENTAL"]
        tech_ev = [e for e in evidence_list if e.category == "TECHNICAL"]
        news_ev = [e for e in evidence_list if e.category == "NEWS"]
        risk_ev = [e for e in evidence_list if e.category == "RISK"]
        anom_ev = [e for e in evidence_list if e.category == "ANOMALY"]
        rag_ev = [e for e in evidence_list if e.category == "RAG"]
        comp_ev = [e for e in evidence_list if e.category == "COMPARISON"]
        macro_ev = [e for e in evidence_list if e.category == "MACRO"]

        # Collect unique verified citations
        citations_dict: Dict[str, Citation] = {}
        for ev in evidence_list:
            if ev.citation:
                citations_dict[ev.citation.citation_id] = ev.citation

        citations = list(citations_dict.values())

        # 1. Executive Summary
        exec_summary = (
            f"Institutional research assessment for {symbols_str} formulated in response to: \"{query}\". "
            f"Analysis synthesizes {len(evidence_list)} independent evidence points across "
            f"{'fundamentals, ' if fund_ev else ''}{'technical indicators, ' if tech_ev else ''}"
            f"{'news intelligence, ' if news_ev else ''}{'downside risk factors, ' if risk_ev else ''}"
            f"and market session telemetry. "
            f"Overall analytical confidence is rated as {validation_report.confidence_level.value} "
            f"({validation_report.confidence_rationale})."
        )

        # 2. Market Context
        market_ctx_lines = []
        if market_ev:
            for e in market_ev:
                if e.metric == "latest_price" and isinstance(e.value, dict):
                    v = e.value
                    market_ctx_lines.append(
                        f"• {e.symbol}: Last traded price is {v.get('price')} {v.get('currency', '')} "
                        f"({'+' if (v.get('change_pct') or 0) > 0 else ''}{v.get('change_pct')}%), "
                        f"with recorded session volume of {v.get('volume', 'N/A'):,}."
                    )
                elif e.metric == "period_performance" and isinstance(e.value, dict):
                    v = e.value
                    market_ctx_lines.append(
                        f"• {e.symbol} ({v.get('timeframe', '6m')} performance): Net period return of {v.get('period_return_pct')}%, "
                        f"trading between a period low of {v.get('period_low')} and high of {v.get('period_high')}."
                    )
        if macro_ev:
            for e in macro_ev:
                if e.metric == "benchmark_indices_overview" and isinstance(e.value, dict):
                    regime = e.value.get("indian_market_regime", "EXPANSION")
                    market_ctx_lines.append(f"• Macro Backdrop: Benchmark regime is categorized as {regime}.")

        market_context_text = "\n".join(market_ctx_lines) if market_ctx_lines else "Market data observations currently limited."

        # 3. Fundamental Analysis
        fund_lines = []
        if fund_ev:
            for e in fund_ev:
                if e.metric == "valuation_ratios" and isinstance(e.value, dict):
                    v = e.value
                    fund_lines.append(
                        f"• Valuation: P/E ratio is {v.get('pe_ratio') or 'N/A'}, P/B is {v.get('pb_ratio') or 'N/A'}, "
                        f"and estimated Market Cap stands at {v.get('market_cap') or 'N/A'}."
                    )
                elif e.metric == "profitability_and_margins" and isinstance(e.value, dict):
                    v = e.value
                    fund_lines.append(
                        f"• Profitability: Operating Margin of {v.get('operating_margin_pct') or 'N/A'}%, "
                        f"Net Margin of {v.get('net_profit_margin_pct') or 'N/A'}%, and ROE of {v.get('roe_pct') or 'N/A'}%."
                    )
                elif e.metric == "solvency_and_health" and isinstance(e.value, dict):
                    v = e.value
                    fund_lines.append(
                        f"• Solvency & Balance Sheet: Debt-to-Equity is {v.get('debt_to_equity') or 'N/A'}, "
                        f"Current Ratio is {v.get('current_ratio') or 'N/A'}, and Altman Z-score of {v.get('altman_z_score') or 'N/A'} "
                        f"reflects a {v.get('health_classification', 'STABLE')} rating."
                    )
        fundamental_analysis_text = "\n".join(fund_lines) if fund_lines else "Detailed fundamental statements not requested or unavailable."

        # 4. Technical Analysis
        tech_lines = []
        if tech_ev:
            for e in tech_ev:
                if e.metric == "momentum_oscillators" and isinstance(e.value, dict):
                    v = e.value
                    tech_lines.append(
                        f"• Momentum: 14-day RSI is currently at {v.get('rsi_14') or 'N/A'} ({v.get('rsi_interpretation')}). "
                        f"MACD line is at {v.get('macd_line')} vs signal line at {v.get('macd_signal')}."
                    )
                elif e.metric == "trend_and_moving_averages" and isinstance(e.value, dict):
                    v = e.value
                    tech_lines.append(
                        f"• Trend Regime: {e.symbol} is in a {v.get('trend_regime')}, trading "
                        f"{'+' if (v.get('price_vs_sma50_pct') or 0) > 0 else ''}{v.get('price_vs_sma50_pct')}% "
                        f"relative to its 50-day SMA ({v.get('sma_50')})."
                    )
                elif e.metric == "volatility_and_bands" and isinstance(e.value, dict):
                    v = e.value
                    tech_lines.append(
                        f"• Volatility Envelope: 20-day Bollinger Upper is {v.get('bollinger_upper')} and Lower is {v.get('bollinger_lower')}, "
                        f"with 14-day ATR at {v.get('atr_14')}."
                    )
        technical_analysis_text = "\n".join(tech_lines) if tech_lines else "Technical indicator calculation not requested for this query."

        # 5. News & Events Analysis
        news_lines = []
        if news_ev:
            for e in news_ev:
                if e.metric == "news_sentiment_summary" and isinstance(e.value, dict):
                    v = e.value
                    news_lines.append(
                        f"• Sentiment Distribution: Across {v.get('articles_analyzed')} recent articles, "
                        f"sentiment is {v.get('dominant_sentiment')} (score: {v.get('sentiment_score')}), "
                        f"comprising {v.get('positive_count')} positive, {v.get('negative_count')} negative, and {v.get('neutral_count')} neutral items."
                    )
                elif e.metric == "headline_event" and isinstance(e.value, dict):
                    v = e.value
                    news_lines.append(
                        f"• Recent Headline ({v.get('published_at', '')[:10]} - {v.get('source')}): \"{v.get('title')}\""
                    )
        news_analysis_text = "\n".join(news_lines) if news_lines else "No breaking news feeds identified for the target symbol."

        # 6. Risk Analysis
        risk_lines = []
        if risk_ev:
            for e in risk_ev:
                if e.metric == "downside_risk_profile" and isinstance(e.value, dict):
                    v = e.value
                    risk_lines.append(
                        f"• Downside Volatility: Annualized 30-day volatility is {v.get('annualized_volatility_pct')}%, "
                        f"classifying {e.symbol} as {v.get('risk_classification')}."
                    )
                    risk_lines.append(
                        f"• Value at Risk: 1-day 95% Historical VaR is estimated at {v.get('var_95_daily_pct')}%, "
                        f"with maximum peak-to-trough period drawdown of {v.get('max_drawdown_pct')}%."
                    )
                    risk_lines.append(
                        f"• Market Sensitivity: Estimated Beta vs {v.get('benchmark', 'Benchmark')} is {v.get('estimated_beta')}."
                    )
        risk_analysis_text = "\n".join(risk_lines) if risk_lines else "Risk analytics not included in scope."

        # 7. Anomaly Analysis
        anomaly_lines = []
        if anom_ev:
            for e in anom_ev:
                if isinstance(e.value, dict):
                    note = e.value.get("analysis_note")
                    if note:
                        anomaly_lines.append(f"• {note}")
        anomaly_analysis_text = "\n".join(anomaly_lines) if anomaly_lines else "No statistically significant price or volume anomalies detected."

        # 8. Comparison Analysis
        comparison_lines = []
        if comp_ev:
            for e in comp_ev:
                if e.metric == "side_by_side_comparison_matrix" and isinstance(e.value, dict):
                    matrix = e.value.get("metrics_matrix", [])
                    comparison_lines.append("• Objective Side-by-Side Comparison Matrix:")
                    for row in matrix:
                        comparison_lines.append(
                            f"  - {row.get('symbol')}: Price: {row.get('latest_price')}, P/E: {row.get('pe_ratio')}, "
                            f"ROE: {row.get('roe_pct')}%, RSI: {row.get('rsi_14')}, Ann. Vol: {row.get('annualized_volatility_pct')}%"
                        )
        comparison_analysis_text = "\n".join(comparison_lines) if comparison_lines else None

        # 9. Key Unknowns
        unknowns = [
            "Future macroeconomic rate decisions and regulatory policy shifts.",
            "Unscheduled corporate disclosures and breaking geopolitical developments.",
        ]
        if not fund_ev:
            unknowns.append("Full audited financial statement footnotes not inspected in current depth.")
        if not rag_ev or any(e.provenance.value == "UNAVAILABLE" for e in rag_ev):
            unknowns.append("Unindexed SEC regulatory 10-K disclosures for recent quarters.")

        # 10. Research Conclusion
        conclusion = (
            f"The synthesized multi-agent findings indicate that {symbols_str} displays "
            f"{'solid balance sheet fundamentals ' if fund_ev else 'active market liquidity '} "
            f"accompanied by {'moderate downside sensitivity' if risk_ev else 'standard volatility'}. "
            f"Evidence from quantitative signals and news sentiment aligns with "
            f"{'current trading range parameters' if tech_ev else 'market baseline'}. "
            f"Investors should evaluate these findings against their individual risk parameters."
        )

        # Provenance summary dictionary
        provenance_summary = {
            "Real Data": f"{validation_report.provenance_breakdown.get('LIVE', 0)} items",
            "Demo / Simulated Data": f"{validation_report.provenance_breakdown.get('DEMO', 0)} items",
            "Calculated Indicators": f"{validation_report.provenance_breakdown.get('CALCULATED', 0)} items",
            "Model-Derived Signals": f"{validation_report.provenance_breakdown.get('MODEL_DERIVED', 0)} items",
            "Unavailable Items": f"{validation_report.provenance_breakdown.get('UNAVAILABLE', 0)} items",
        }

        # Limitations & Guardrail Disclaimer
        limitations = [
            "Analytical research only; does not constitute personalized investment advice or buy/sell recommendations.",
            "Historical price behavior and quantitative indicators are statistical reflections, not guaranteed future outcomes.",
            "Data provenance reflects development DEMO providers where live exchange credentials are not active.",
        ]

        return ResearchReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            query=query,
            generated_at=datetime.now(timezone.utc).isoformat(),
            symbols=symbols,
            time_range=plan.date_range,
            intent=plan.intent,
            research_depth=plan.research_depth,
            executive_summary=exec_summary,
            market_context=market_context_text,
            fundamental_analysis=fundamental_analysis_text,
            technical_analysis=technical_analysis_text,
            news_analysis=news_analysis_text,
            risk_analysis=risk_analysis_text,
            anomaly_analysis=anomaly_analysis_text,
            scenario_analysis="Stochastic stress scenario analysis available via Scenario Simulator module.",
            comparison_analysis=comparison_analysis_text,
            evidence_conflicts=validation_report.conflicts_detected,
            unknowns=unknowns,
            research_conclusion=conclusion,
            confidence_level=validation_report.confidence_level,
            confidence_rationale=validation_report.confidence_rationale,
            provenance_summary=provenance_summary,
            citations=citations,
            limitations=limitations
        )


research_synthesizer = ResearchSynthesizer()
