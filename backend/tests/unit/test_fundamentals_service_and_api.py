"""
MarketMind AI — Unit & Integration Tests for Fundamentals Service, Collector & API Endpoints.
Phase 6.6: Tests service caching, batch collection, failure isolation, health telemetry,
API responses, and AI agent tool integrations.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.fundamentals_service import fundamentals_service
from app.services.fundamentals_collector import fundamentals_collector
from app.agents.tools import (
    tool_get_fundamentals,
    tool_get_fundamental_analysis,
    tool_get_financial_statements,
)


@pytest.mark.asyncio
async def test_1_fundamentals_service_overview():
    overview = await fundamentals_service.get_overview("RELIANCE.NS")
    assert overview is not None
    assert overview.symbol == "RELIANCE.NS"
    assert overview.valuation.pe_ratio is not None
    assert overview.profitability.gross_margin_pct is not None


@pytest.mark.asyncio
async def test_2_fundamentals_service_statements():
    inc = await fundamentals_service.get_statements("TCS.NS", statement_type="income", period_type="annual")
    assert inc.statement_type == "income"
    assert len(inc.periods) > 0
    assert inc.periods[0].get("revenue") is not None

    bal = await fundamentals_service.get_statements("TCS.NS", statement_type="balance_sheet", period_type="annual")
    assert bal.statement_type == "balance_sheet"
    assert len(bal.periods) > 0

    cf = await fundamentals_service.get_statements("TCS.NS", statement_type="cash_flow", period_type="annual")
    assert cf.statement_type == "cash_flow"
    assert len(cf.periods) > 0


@pytest.mark.asyncio
async def test_3_fundamentals_service_company_profile():
    profile = await fundamentals_service.get_company_profile("AAPL")
    assert profile is not None
    assert profile.symbol == "AAPL"
    assert profile.exchange == "NASDAQ"
    assert profile.country == "US"
    assert profile.currency == "USD"


@pytest.mark.asyncio
async def test_4_fundamentals_collector_batch_and_error_isolation():
    # Test batch collection with both valid and arbitrary symbols
    universe = ["INFY.NS", "AAPL", "NONEXISTENT_XYZ_123"]
    res = await fundamentals_collector.collect_universe(universe)
    assert res["total_symbols"] == 3
    # Valid symbols succeeded
    assert res["processed"] >= 2

    health = fundamentals_collector.get_health_report()
    assert health["status"] in ["HEALTHY", "DEGRADED"]
    assert health["records_processed"] >= 2
    assert "INDIAN_PROVIDER" in health["provider_status"]


@pytest.mark.asyncio
async def test_5_ai_agent_fundamental_tools():
    # 1. tool_get_fundamentals
    data = await tool_get_fundamentals("RELIANCE.NS")
    assert "symbol" in data or "ticker" in data
    assert "valuation" in data

    # 2. tool_get_fundamental_analysis (separating facts, calculations, assumptions)
    analysis = await tool_get_fundamental_analysis("TCS.NS")
    assert "facts" in analysis
    assert "calculations" in analysis
    assert "assumptions" in analysis
    assert "data_provenance" in analysis
    assert analysis["data_provenance"]["status"] in ["DEMO", "LIVE"]

    # 3. tool_get_financial_statements
    stmts = await tool_get_financial_statements("INFY.NS", "income", "annual")
    assert "periods" in stmts
    assert len(stmts["periods"]) > 0


def test_6_api_endpoints():
    client = TestClient(app)

    # 1. GET /api/v1/fundamentals/health
    res_health = client.get("/api/v1/fundamentals/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert "status" in data_health
    assert "records_processed" in data_health

    # 2. GET /api/v1/fundamentals/{symbol}
    res_fund = client.get("/api/v1/fundamentals/RELIANCE.NS")
    assert res_fund.status_code == 200
    data_fund = res_fund.json()
    assert data_fund["symbol"] == "RELIANCE.NS"
    assert "valuation" in data_fund
    assert "profitability" in data_fund
    assert "financial_health" in data_fund

    # 3. GET /api/v1/fundamentals/{symbol}/statements
    res_stmts = client.get("/api/v1/fundamentals/RELIANCE.NS/statements?statement_type=income&period_type=annual")
    assert res_stmts.status_code == 200
    data_stmts = res_stmts.json()
    assert data_stmts["statement_type"] == "income"
    assert len(data_stmts["periods"]) > 0

    # 4. GET /api/v1/fundamentals/{symbol}/profile
    res_prof = client.get("/api/v1/fundamentals/RELIANCE.NS/profile")
    assert res_prof.status_code == 200
    data_prof = res_prof.json()
    assert data_prof["symbol"] == "RELIANCE.NS"
    assert data_prof["currency"] == "INR"

    # 5. GET /api/v1/stocks/{symbol}/financials
    res_fin = client.get("/api/v1/stocks/AAPL/financials?statement_type=income&period_type=annual")
    assert res_fin.status_code == 200
    data_fin = res_fin.json()
    assert data_fin["statement_type"] == "income"
    assert len(data_fin["periods"]) > 0

    # 6. GET /api/v1/stocks/{symbol}/ratios
    res_rat = client.get("/api/v1/stocks/AAPL/ratios")
    assert res_rat.status_code == 200
    data_rat = res_rat.json()
    assert "valuation" in data_rat
    assert "profitability" in data_rat
    assert "leverage" in data_rat
