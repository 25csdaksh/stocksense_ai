# MARKETMIND AI
### AI-Powered Stock Market Intelligence & Scenario Analysis Platform

[![Platform](https://img.shields.io/badge/Platform-MARKETMIND_AI-0A4D3C.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-Academic_Research-C5A059.svg)](#)

---

## 🏛️ Executive Summary

**MARKETMIND AI** is a production-quality academic platform combining **quantitative machine learning**, **econometric modeling**, **semantic RAG**, and **multi-agent orchestration** for deep financial market intelligence and probabilistic scenario stress testing.

> **Regulatory & Academic Notice**: MARKETMIND AI is engineered strictly for educational and analytical research purposes. It does not provide investment advice, financial planning, or guaranteed price targets. All scenario projections, Value-at-Risk (VaR) estimates, and factor scores are probabilistic representations of statistical models.

---

## ⚡ Key Capabilities & Core Features

1. **Executive Market Pulse Dashboard**: Real-time index tracking, sector rotation momentum matrix, and live statistical anomaly streaming.
2. **Deep Stock Intelligence Workspace**: High-frequency TradingView Lightweight candlestick charts with SMA/EMA/VWAP overlays, valuation multiples, profitability scorecards, and SEC 10-K disclosures.
3. **Merton Jump-Diffusion Scenario Simulator**: 10,000-path stochastic Monte Carlo engine with Poisson jumps, computing empirical VaR (95%/99%) and CVaR (Expected Shortfall).
4. **Historical Crisis Stress Tester**: Replays portfolio and equity drawdowns across major macro crises (2008 Lehman Collapse, 2020 COVID Flash Crash, 2022 Fed Rate Hiking Shock, 2000 Dot-com Bubble).
5. **Macroeconomic Sensitivity Engine**: Multi-variable shock modeling across interest rates ($\Delta$ bps), CPI inflation ($\Delta$%), crude oil ($\Delta$%), and real GDP growth ($\Delta$%).
6. **5-Factor Stock DNA Profiler**: Multi-factor radar visualization quantifying Value, Growth, Quality, Momentum, and Low Volatility dimensions.
7. **Market Contagion & Relationship Network**: NetworkX graph mapping systemic eigenvector centrality hubs and Granger causality lead-lag predictive dynamics.
8. **Financial RAG Knowledge Engine**: Qdrant dense vector retrieval over SEC 10-K and 10-Q regulatory filings with verbatim citation page tracking.
9. **LangGraph Multi-Agent Studio**: Streaming Server-Sent Events (SSE) AI co-pilot with transparent thought-step logs, tool execution badges, and inline chart rendering.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14+ (App Router), TypeScript, Tailwind CSS, Lightweight Charts (TradingView), Recharts, Lucide React |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2, Async SQLAlchemy 2.0, HTTPX, Server-Sent Events (SSE), WebSockets |
| **AI Multi-Agent** | Google Gemini API, LangChain, LangGraph StateGraph, Tool Sandbox |
| **Quantitative ML** | NumPy, Pandas, SciPy, Scikit-learn (Isolation Forest, KMeans), Statsmodels (Granger Causality), GARCH(1,1), NetworkX |
| **RAG Knowledge** | Qdrant Vector Database, BAAI/bge-base embeddings, PyPDF |
| **Databases & Cache**| PostgreSQL 16 + TimescaleDB Hypertables, Redis 7 (TTL caching & Pub/Sub) |
| **Infrastructure** | Docker, Docker Compose, Multi-stage builds, Healthchecks |

---

## 📐 Monorepo Architecture

```
marketmind-ai/
├── frontend/                     # Next.js 14+ Light-Theme Financial Terminal
│   ├── src/app/                  # App Router Pages (Dashboard, Workspace, Simulator, etc.)
│   ├── src/components/           # Charts (TradingView, Fan Chart, Radar) & Agent Chat
│   ├── src/lib/                  # API Gateway Client & Stream Parsers
│   └── src/types/                # Shared TypeScript Type Definitions
│
├── backend/                      # FastAPI Microservice Gateway
│   ├── main.py                   # Application Entrypoint & WebSocket Tick Feeds
│   ├── config.py                 # Pydantic Settings & Environment Validations
│   ├── api/v1/                   # Modular REST Routers (Market, Analytics, Scenario, RAG)
│   ├── core/                     # Database, Redis, Logger, and Guardrails
│   ├── models/                   # TimescaleDB & PostgreSQL ORM Models
│   ├── schemas/                  # Pydantic v2 Data Transfer Objects
│   └── services/                 # Business Logic, Data Ingestion, RAG, and Agent Runner
│
├── ml-engine/                    # Standalone Quantitative Machine Learning Package
│   ├── anomaly/                  # Isolation Forest, GARCH(1,1), and Volume Spike Detectors
│   ├── correlation/              # Rolling Pearson/Spearman, Granger Causality, NetworkX Graph
│   ├── scenario/                 # Merton Jump Diffusion, Historical Crises, Macro Shocks
│   ├── dna/                      # 5-Factor Stock DNA Profiler & Peer Clusterer
│   └── engine.py                 # Unified MLEngine Facade
│
├── docker/                       # Dockerfiles & Database Initialization Scripts
├── tests/                        # Automated ML and FastAPI Integration Test Suites
├── docker-compose.yml            # Multi-container Ecosystem Orchestration
└── README.md                     # Documentation
```

---

## 🚀 Quick Start & Deployment

### Option A: Running via Docker Compose (Single Command)

```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Launch all 5 containers (TimescaleDB, Redis, Qdrant, Backend, Frontend)
docker-compose up --build -d

# 3. Access applications:
# Frontend Terminal:  http://localhost:3000
# Backend OpenAPI:    http://localhost:8000/docs
# Qdrant Dashboard:   http://localhost:6333/dashboard
```

### Option B: Running Locally for Development

#### 1. Backend & ML Engine
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8000
```

#### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
# Dashboard runs on http://localhost:3000
```

---

## 🧪 Verification & Test Suite

Run the full automated test suite verifying mathematical models and API endpoints:

```bash
# Run Quantitative & ML Unit Tests
python tests/test_ml_engine.py

# Run FastAPI Integration Tests
python tests/test_api.py
```
