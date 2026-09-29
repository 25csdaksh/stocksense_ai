"""
Company Fundamentals & Stock DNA Endpoints.
"""
from fastapi import APIRouter, HTTPException
from schemas.analytics_schema import StockDNAResponse
from services.market_data_service import market_data_service, SUPPORTED_UNIVERSE

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-engine")))
from engine import ml_engine

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals & Stock DNA"])


@router.get("/overview/{ticker}")
async def get_fundamental_overview(ticker: str):
    """Returns normalized valuation multiples, growth metrics, and capital structure scorecard."""
    ticker = ticker.upper()
    meta = SUPPORTED_UNIVERSE.get(ticker, {
        "name": ticker,
        "sector": "Information Technology",
        "pe": 28.5,
        "pb": 6.4,
        "div_yield": 0.01,
        "beta": 1.10
    })

    return {
        "ticker": ticker,
        "name": meta["name"],
        "sector": meta["sector"],
        "valuation": {
            "pe_ratio": meta.get("pe", 28.5),
            "forward_pe": round(meta.get("pe", 28.5) * 0.88, 2),
            "pb_ratio": meta.get("pb", 6.4),
            "ev_ebitda": 22.4,
            "fcf_yield_pct": 3.8
        },
        "profitability": {
            "gross_margin_pct": 68.5,
            "operating_margin_pct": 34.2,
            "net_margin_pct": 26.8,
            "roe_pct": 38.4,
            "roa_pct": 16.2
        },
        "financial_health": {
            "current_ratio": 1.45,
            "debt_to_equity": 0.62,
            "interest_coverage_ratio": 18.5,
            "altman_z_score": 4.85,
            "health_score": "EXCELLENT"
        }
    }


@router.get("/dna/{ticker}", response_model=StockDNAResponse)
async def get_stock_dna(ticker: str):
    """Computes 5-Factor Stock DNA Vector (Value, Growth, Quality, Momentum, Low Volatility) for radar visualization."""
    ticker = ticker.upper()
    quote = market_data_service.get_quote(ticker)
    meta = SUPPORTED_UNIVERSE.get(ticker, {"pe": 28.5, "pb": 6.0, "div_yield": 0.01, "beta": 1.10})

    dna = ml_engine.calculate_stock_dna(
        ticker=ticker,
        fundamentals={
            "pe_ratio": meta.get("pe", 28.5),
            "pb_ratio": meta.get("pb", 6.0),
            "dividend_yield": meta.get("div_yield", 0.01),
            "roe": 0.32,
            "roa": 0.14,
            "debt_to_equity": 0.65,
            "revenue_growth_yoy": 0.18,
            "net_income_growth_yoy": 0.22
        },
        price_metrics={
            "beta": meta.get("beta", 1.10),
            "annualized_volatility": 26.0,
            "return_3m_pct": quote["change_pct"] * 4.5,
            "return_1y_pct": quote["change_pct"] * 12.0
        }
    )

    return dna
