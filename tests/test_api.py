"""
Integration Tests for MARKETMIND AI FastAPI Endpoints.
"""
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "MARKETMIND" in data["service"]


def test_market_assets():
    response = client.get("/api/v1/market/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) > 0
    tickers = [a["ticker"] for a in assets]
    assert "AAPL" in tickers
    assert "NVDA" in tickers


def test_market_quote():
    response = client.get("/api/v1/market/quote/NVDA")
    assert response.status_code == 200
    quote = response.json()
    assert quote["ticker"] == "NVDA"
    assert quote["price"] > 0
    assert "data_source" in quote


def test_stock_dna():
    response = client.get("/api/v1/fundamentals/dna/AAPL")
    assert response.status_code == 200
    dna = response.json()
    assert dna["ticker"] == "AAPL"
    assert len(dna["radar_data"]) == 5
    assert "dominant_persona" in dna


def test_anomalies_stream():
    response = client.get("/api/v1/analytics/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert "systemic_stress_index" in data


def test_scenario_monte_carlo():
    payload = {
        "ticker": "NVDA",
        "days": 30,
        "iterations": 1000,
        "drift_annualized": 0.08,
        "volatility_annualized": 0.28,
        "jump_intensity": 0.05
    }
    response = client.post("/api/v1/scenario/monte-carlo", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["ticker"] == "NVDA"
    assert "fan_chart" in result
    assert "value_at_risk_95_pct" in result
    assert "Disclaimer" in result["disclaimer"]


def test_rag_sec_search():
    payload = {
        "query": "TSMC advanced packaging supply chain risk",
        "ticker": "NVDA",
        "top_k": 3
    }
    response = client.post("/api/v1/research/search-filings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "citations" in data
    assert len(data["citations"]) > 0
    first_c = data["citations"][0]
    assert first_c["ticker"] == "NVDA"
    assert "page_number" in first_c


def test_agent_query():
    payload = {
        "query": "Simulate a 90-day Monte Carlo scenario on AAPL",
        "session_id": "test_session_1"
    }
    response = client.post("/api/v1/agent/query", json=payload)
    assert response.status_code == 200
    agent_res = response.json()
    assert "thought_steps" in agent_res
    assert len(agent_res["thought_steps"]) > 0
    assert "answer" in agent_res
    assert "Disclaimer & Regulatory Notice" in agent_res["answer"]


if __name__ == "__main__":
    test_health_check()
    test_market_assets()
    test_market_quote()
    test_stock_dna()
    test_anomalies_stream()
    test_scenario_monte_carlo()
    test_rag_sec_search()
    test_agent_query()
    print("All FastAPI integration tests passed successfully!")
