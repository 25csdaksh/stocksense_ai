"""
End-to-End API Integration Suite for MarketMind AI.
Verifies all 25+ primary REST endpoints across the full stack:
Request -> Route -> Service -> Repository -> Database -> Response.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def auth_credentials(test_client: TestClient):
    """Registers and authenticates a test user, returning the JWT authorization headers."""
    user_payload = {
        "username": "e2e_lead_analyst",
        "email": "e2e_lead@marketmind.ai",
        "password": "E2ePassword999!",
        "full_name": "E2E Lead Analyst"
    }
    test_client.post("/api/v1/auth/register", json=user_payload)
    login = test_client.post("/api/v1/auth/login", json={
        "username": user_payload["username"],
        "password": user_payload["password"]
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. System Health & Auth Endpoints
# ==============================================================================

def test_e2e_health(test_client: TestClient):
    resp = test_client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_e2e_auth_me(test_client: TestClient, auth_credentials: dict):
    resp = test_client.get("/api/v1/auth/me", headers=auth_credentials)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "e2e_lead_analyst"


# ==============================================================================
# 2. Market Overview & Indices Endpoints
# ==============================================================================

def test_e2e_market_overview(test_client: TestClient):
    resp = test_client.get("/api/v1/market/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "market_regime" in data or "indices" in data or "sectors" in data


def test_e2e_market_indices(test_client: TestClient):
    resp = test_client.get("/api/v1/market/indices")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


# ==============================================================================
# 3. Stocks & Historical OHLCV Endpoints
# ==============================================================================

def test_e2e_stocks_list(test_client: TestClient):
    resp = test_client.get("/api/v1/stocks")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    symbols = [s["ticker"] for s in data]
    assert "AAPL" in symbols or "NVDA" in symbols


def test_e2e_stock_detail(test_client: TestClient):
    resp = test_client.get("/api/v1/stocks/AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert "price" in data or "name" in data


def test_e2e_stock_history(test_client: TestClient):
    resp = test_client.get("/api/v1/stocks/NVDA/history?timeframe=1m")
    assert resp.status_code == 200
    data = resp.json()
    assert "bars" in data
    assert len(data["bars"]) > 0
    first_bar = data["bars"][0]
    assert "time" in first_bar
    assert "close" in first_bar


# ==============================================================================
# 4. Fundamentals & Financial Statements Endpoints
# ==============================================================================

def test_e2e_fundamentals(test_client: TestClient):
    resp = test_client.get("/api/v1/fundamentals/MSFT")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "MSFT"
    assert "valuation" in data
    assert "profitability" in data


# ==============================================================================
# 5. Financial News Endpoints
# ==============================================================================

def test_e2e_news_feed(test_client: TestClient):
    resp = test_client.get("/api/v1/news")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_e2e_news_by_symbol(test_client: TestClient):
    resp = test_client.get("/api/v1/news/NVDA")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "NVDA"
    assert "overall_sentiment" in data
    assert "news_items" in data
    assert isinstance(data["news_items"], list)


# ==============================================================================
# 6. Quantitative Analytics Endpoints
# ==============================================================================

def test_e2e_analytics_technical(test_client: TestClient):
    resp = test_client.get("/api/v1/analytics/AAPL/technical")
    assert resp.status_code == 200
    data = resp.json()
    assert "rsi_14" in data
    assert "technical_bias" in data


def test_e2e_analytics_correlations(test_client: TestClient):
    resp = test_client.get("/api/v1/analytics/correlations")
    assert resp.status_code == 200
    data = resp.json()
    assert "matrix" in data
    assert "assets" in data


def test_e2e_analytics_dna(test_client: TestClient):
    resp = test_client.get("/api/v1/analytics/AAPL/dna")
    assert resp.status_code == 200
    data = resp.json()
    assert "factor_scores" in data
    assert "dominant_persona" in data


# ==============================================================================
# 7. Anomaly Detection Endpoint
# ==============================================================================

def test_e2e_anomalies(test_client: TestClient):
    resp = test_client.get("/api/v1/anomalies")
    assert resp.status_code == 200
    data = resp.json()
    assert "anomalies" in data
    assert "systemic_stress_index" in data


# ==============================================================================
# 8. Scenario Analysis Endpoints
# ==============================================================================

def test_e2e_scenario_monte_carlo(test_client: TestClient):
    payload = {
        "ticker": "AAPL",
        "days": 60,
        "iterations": 500
    }
    resp = test_client.post("/api/v1/scenarios/monte-carlo", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "expected_terminal_price_p50" in data
    assert "value_at_risk_95_pct" in data


def test_e2e_scenario_historical_stress(test_client: TestClient):
    payload = {
        "ticker": "NVDA"
    }
    resp = test_client.post("/api/v1/scenarios/historical-stress", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario_results" in data


def test_e2e_scenario_macro_shock(test_client: TestClient):
    payload = {
        "ticker": "AAPL",
        "rate_shock_bps": 100.0,
        "oil_shock_pct": 20.0
    }
    resp = test_client.post("/api/v1/scenarios/macro-shock", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "projected_price" in data
    assert "total_projected_return_pct" in data


# ==============================================================================
# 9. Portfolio & Watchlist Endpoints
# ==============================================================================

def test_e2e_portfolio_management(test_client: TestClient, auth_credentials: dict):
    # 1. Fetch current portfolio
    get_resp = test_client.get("/api/v1/portfolio", headers=auth_credentials)
    assert get_resp.status_code == 200

    # 2. Record a BUY transaction
    tx_payload = {
        "ticker": "AAPL",
        "shares": 25.0,
        "price": 182.50,
        "transaction_type": "BUY"
    }
    tx_resp = test_client.post("/api/v1/portfolio/transactions", json=tx_payload, headers=auth_credentials)
    assert tx_resp.status_code == 200


def test_e2e_watchlist_management(test_client: TestClient, auth_credentials: dict):
    # 1. Add symbol to watchlist
    add_resp = test_client.post("/api/v1/watchlist", json={"ticker": "NVDA"}, headers=auth_credentials)
    assert add_resp.status_code == 201

    # 2. Get watchlist
    get_resp = test_client.get("/api/v1/watchlist", headers=auth_credentials)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert isinstance(data, list)


# ==============================================================================
# 10. Research RAG & AI Multi-Agent Endpoints
# ==============================================================================

def test_e2e_research_query(test_client: TestClient):
    payload = {
        "query": "Supply chain dependencies and semiconductor foundry partners",
        "ticker": "NVDA",
        "top_k": 3
    }
    resp = test_client.post("/api/v1/research/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "citations" in data
    assert "synthesis_summary" in data


def test_e2e_ai_analyze_orchestration(test_client: TestClient):
    payload = {
        "query": "Assess Microsoft Azure growth trajectory and cloud margin outlook",
        "session_id": "e2e_msft_analysis"
    }
    resp = test_client.post("/api/v1/ai/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "thought_steps" in data
    assert "citations" in data
