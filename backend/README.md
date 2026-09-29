# MarketMind AI — Backend Platform

> **AI-Powered Stock Market Intelligence, RAG SEC Retrieval & Stochastic Scenario Analysis Platform**

---

## 1. Overview & Technology Stack

MarketMind AI backend is an enterprise-grade quantitative analytics and multi-agent AI system built using **FastAPI**, **Pydantic v2**, **NumPy**, **Pandas**, **SciPy**, **Scikit-learn**, **Statsmodels**, **NetworkX**, and **LangGraph**.

### Core Stack:
- **Web Framework**: FastAPI (Async ASGI, OpenAPI / Swagger documentation)
- **Validation**: Pydantic v2 & Pydantic Settings
- **Quantitative Engine**: NumPy, Pandas, SciPy, Scikit-learn (IsolationForest), Statsmodels (GARCH, Granger Causality), NetworkX (Eigenvector Centrality)
- **Multi-Agent Orchestrator**: LangGraph StateGraph pipeline with Server-Sent Events (SSE) streaming
- **RAG Engine**: Cosine similarity & lexical vector retriever with pre-indexed SEC Form 10-K regulatory filings
- **Caching & Storage Layer**: Async Redis client with transparent zero-dependency in-memory TTL dictionary fallback
- **Authentication**: JWT Bearer tokens with HMAC-SHA256 password hashing

---

## 2. Directory Architecture

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entry point, CORS, lifecycle hooks
│   │
│   ├── core/                       # Core configuration, security, logging, exceptions
│   │   ├── config.py               # Pydantic BaseSettings loading from .env
│   │   ├── security.py             # JWT token encoding/decoding & HMAC password hashing
│   │   ├── logging.py              # Structured JSON logging system
│   │   └── exceptions.py           # Domain exception hierarchy and centralized handlers
│   │
│   ├── api/                        # API routes and dependency injection
│   │   ├── dependencies.py         # Auth tokens and Redis cache dependencies
│   │   └── routes/
│   │       ├── auth.py             # User registration, login, JWT issuance, profile
│   │       ├── market.py           # Regime detection, benchmark indices, sector weights
│   │       ├── stocks.py           # Universe listing, real-time quotes, OHLCV bars
│   │       ├── fundamentals.py     # Valuation multiples, profitability, financial statements
│   │       ├── news.py             # Real-time market feed, ticker news with sentiment
│   │       ├── analytics.py        # Technical indicators, correlation matrix, network graph, Stock DNA
│   │       ├── anomalies.py        # Isolation Forest anomalies, GARCH volatility regimes
│   │       ├── scenarios.py        # Merton Jump Diffusion Monte Carlo, historical stress, macro shocks
│   │       ├── portfolio.py        # Portfolio holdings, transaction ingestion, portfolio stress tests
│   │       ├── watchlist.py        # Watchlist management (add, list, delete)
│   │       ├── research.py         # RAG semantic search across SEC 10-K regulatory filings
│   │       ├── ai.py               # Multi-agent reasoning queries & real-time SSE streaming
│   │       └── health.py           # System uptime, telemetry, component health probes
│   │
│   ├── schemas/                    # Pydantic request/response validation schemas
│   │   ├── auth.py
│   │   ├── market.py
│   │   ├── stock.py
│   │   ├── fundamentals.py
│   │   ├── news.py
│   │   ├── analytics.py
│   │   ├── anomaly.py
│   │   ├── scenario.py
│   │   ├── portfolio.py
│   │   ├── research.py
│   │   └── ai.py
│   │
│   ├── services/                   # Business logic layer (routes -> services -> quant/agents)
│   │   ├── market_service.py
│   │   ├── stock_service.py
│   │   ├── fundamentals_service.py
│   │   ├── news_service.py
│   │   ├── analytics_service.py
│   │   ├── anomaly_service.py
│   │   ├── scenario_service.py
│   │   ├── portfolio_service.py
│   │   ├── research_service.py
│   │   └── ai_service.py
│   │
│   ├── providers/                  # Abstracted data providers with synthetic dev fallbacks
│   │   ├── market_data/            # BaseProvider, YFinanceProvider, MockMarketDataProvider
│   │   ├── news/                   # BaseNewsProvider, MockNewsProvider
│   │   └── fundamentals/           # BaseFundamentalsProvider, MockFundamentalsProvider
│   │
│   ├── analytics/                  # Pure quantitative & econometric algorithms
│   │   ├── technical.py            # SMA, EMA, RSI, MACD, Bollinger Bands, ATR, VWAP, Realized Vol
│   │   ├── anomaly.py              # Isolation Forest, GARCH(1,1) MLE, Volume Spike Detector
│   │   ├── correlation.py          # Rolling correlation matrix, CAPM beta, Granger causality, Contagion Graph
│   │   ├── scenario.py             # Merton Jump Diffusion Monte Carlo, Historical Stress (GFC, COVID), Macro Elasticity
│   │   └── stock_dna.py            # 5-Factor scoring (Value, Growth, Quality, Momentum, Low Volatility)
│   │
│   ├── agents/                     # LangGraph multi-agent cognitive architecture
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── tools.py                # Tool functions for quant engines, quotes, news, SEC filings
│   │   ├── nodes.py                # Supervisor, Data Fetcher, Quant Engine, RAG, Synthesis nodes
│   │   └── graph.py                # MultiAgentGraphRunner & SSE Stream Generator
│   │
│   ├── rag/                        # Retrieval-Augmented Generation subsystem
│   │   ├── embeddings.py           # Embedding interface
│   │   ├── ingestion.py            # Semantic chunker & metadata parser
│   │   ├── retrieval.py            # Hybrid lexical/cosine vector retriever with preloaded SEC 10-Ks
│   │   └── context.py              # Prompt citation builder
│   │
│   ├── cache/                      # Redis client with in-memory TTL dictionary fallback
│   │   └── redis_client.py
│   │
│   └── utils/                      # Shared helpers, validators, and constants
│       ├── constants.py            # Supported universe, sector maps, financial disclaimer
│       ├── validators.py           # Ticker, timeframe, interval, Monte Carlo validators
│       └── helpers.py              # Math, date formatting, NaN cleaners
│
├── tests/                          # Automated Pytest suite
│   ├── test_health.py
│   ├── test_validation.py
│   ├── test_technical.py
│   ├── test_anomaly.py
│   ├── test_correlation.py
│   ├── test_scenario.py
│   ├── test_services.py
│   └── test_ai_validation.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 3. REST API Endpoint Catalog

All routes are versioned under `/api/v1/`.

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | `GET` | `/health` | Root health probe |
| **Health** | `GET` | `/api/v1/health` | Subsystem telemetry & component health |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user account |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate and issue JWT Bearer token |
| **Auth** | `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile |
| **Market** | `GET` | `/api/v1/market/overview` | Global market regime, benchmark indices, top movers |
| **Market** | `GET` | `/api/v1/market/indices` | S&P 500, Nasdaq 100, Dow Jones, Russell 2000, VIX |
| **Market** | `GET` | `/api/v1/market/sectors` | Sector performance and momentum rankings |
| **Stocks** | `GET` | `/api/v1/stocks` | Supported universe asset directory |
| **Stocks** | `GET` | `/api/v1/stocks/{symbol}` | Real-time quote, market cap, 52-week range |
| **Stocks** | `GET` | `/api/v1/stocks/{symbol}/history` | Historical OHLCV candlestick time series |
| **Fundamentals** | `GET` | `/api/v1/fundamentals/{symbol}` | Valuation multiples, profitability, financial health |
| **Fundamentals** | `GET` | `/api/v1/fundamentals/{symbol}/statements` | Multi-period income, balance sheet, cash flows |
| **News** | `GET` | `/api/v1/news` | Market-wide news feed with NLP sentiment |
| **News** | `GET` | `/api/v1/news/{symbol}` | Company news with aggregate sentiment score |
| **Analytics** | `GET` | `/api/v1/analytics/{symbol}/technical` | SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Vol |
| **Analytics** | `GET` | `/api/v1/analytics/correlations` | Rolling cross-asset return correlation matrix |
| **Analytics** | `GET` | `/api/v1/analytics/relationship-graph` | NetworkX contagion graph with eigenvector centrality |
| **Analytics** | `GET` | `/api/v1/analytics/{symbol}/dna` | 5-Factor Stock DNA radar profile (0–100 scale) |
| **Anomalies** | `GET` | `/api/v1/anomalies` | Cross-universe multivariate anomaly stream |
| **Anomalies** | `GET` | `/api/v1/anomalies/{symbol}` | Isolation Forest, GARCH volatility, volume spikes |
| **Scenarios** | `POST` | `/api/v1/scenarios/monte-carlo` | Merton Jump Diffusion simulation (VaR/CVaR, fan chart) |
| **Scenarios** | `POST` | `/api/v1/scenarios/historical-stress` | Crisis replay (2008 GFC, 2020 COVID, 2022 Rates, 2000 Tech) |
| **Scenarios** | `POST` | `/api/v1/scenarios/macro-shock` | Multi-variable macro factor shock (Rates, CPI, Oil, GDP) |
| **Portfolio** | `GET` | `/api/v1/portfolio` | Portfolio holdings, market value, weighted beta, 95% VaR |
| **Portfolio** | `POST` | `/api/v1/portfolio/transactions` | Ingest BUY / SELL transactions |
| **Portfolio** | `POST` | `/api/v1/portfolio/stress-test` | Multi-crisis historical stress test on portfolio holdings |
| **Watchlist** | `GET` | `/api/v1/watchlist` | User watchlist with live quotes |
| **Watchlist** | `POST` | `/api/v1/watchlist` | Add ticker to watchlist |
| **Watchlist** | `DELETE` | `/api/v1/watchlist/{symbol}` | Remove ticker from watchlist |
| **Research** | `POST` | `/api/v1/research/query` | RAG hybrid retrieval against SEC 10-K filings |
| **Research** | `GET` | `/api/v1/research/filings/{symbol}` | Retrieve indexed filing sections for a company |
| **AI** | `POST` | `/api/v1/ai/analyze` | Multi-agent reasoning pipeline execution |
| **AI** | `GET` | `/api/v1/ai/stream` | Real-time Server-Sent Events (SSE) streaming |

---

## 4. Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run FastAPI Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Run Automated Test Suite
```bash
pytest tests -v
```
