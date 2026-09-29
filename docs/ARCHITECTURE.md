# MARKETMIND AI — Architecture Deep Dive

## 1. System High-Level Topology

MARKETMIND AI adopts a modular microservice architecture split into three distinct subsystems:
- **Presentation Layer**: Next.js 14 App Router terminal with TradingView Lightweight Charts & Server-Sent Events client.
- **API Gateway & Agent Hub**: FastAPI REST/SSE endpoints with Pydantic v2 validation, LangGraph StateGraph agent execution, and structured logging.
- **Quantitative ML & Knowledge Layer**: Standalone econometric/ML algorithms (Merton Jump Diffusion, GARCH, Isolation Forest, Factor DNA) coupled with Qdrant vector retrieval.

```
                      +-----------------------------+
                      |   Client Web Browser        |
                      |   (Next.js 14 App Router)   |
                      +--------------+--------------+
                                     |
                                     | REST / SSE / WebSockets
                                     v
                      +-----------------------------+
                      |   FastAPI Gateway Server    |
                      |   - Route Handlers          |
                      |   - Guardrails & Policies   |
                      |   - LangGraph Agent Hub     |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
+---------------------+   +---------------------+   +---------------------+
| PostgreSQL 16 +     |   | Qdrant Vector DB    |   | Redis 7             |
| TimescaleDB         |   | - SEC 10-K Filings  |   | - Micro-Tick Cache  |
| - Hypertables:      |   | - Transcripts       |   | - Session Checkpoint|
|   OHLCV Time Series |   | - Dense Embeddings  |   | - Rate Limits       |
+---------------------+   +---------------------+   +---------------------+
```

---

## 2. Quantitative ML Engine Architecture

### Merton Jump-Diffusion Process
Price dynamics are modeled using:
$$dS_t = (\mu - \lambda k) S_t dt + \sigma S_t dW_t + J_t S_t dN_t$$
where:
- $\mu$: Annualized expected drift.
- $\sigma$: Annualized Brownian diffusion volatility.
- $N_t$: Poisson process with jump intensity $\lambda$.
- $J_t$: Log-normal jump magnitude $\ln(1 + J_t) \sim \mathcal{N}(\mu_J, \sigma_J^2)$.
- $k = \exp(\mu_J + 0.5\sigma_J^2) - 1$: Compensator ensuring martingale consistency.

### Value at Risk (VaR) & Conditional VaR (Expected Shortfall)
- **Empirical VaR ($1 - \alpha$)**:
  $$\text{VaR}_\alpha = -\inf \{ r \in \mathbb{R} : P(R \le r) \ge \alpha \}$$
- **Conditional VaR (CVaR)**:
  $$\text{CVaR}_\alpha = \mathbb{E}[R \mid R \le -\text{VaR}_\alpha]$$

---

## 3. Financial RAG Pipeline & Citation Provenance

```
SEC EDGAR 10-K / 10-Q PDFs
         |
         v
Recursive Semantic Chunker (512-1024 tokens, 10% overlap)
         |
         v
Dense Vector Embedding (BAAI/bge-base / Gemini text-embedding-004)
         |
         v
Qdrant Vector Database (Cosine Metric + HNSW Index)
         |
         v
Cross-Encoder Semantic Re-Ranker
         |
         v
Synthesis with Exact Document, Fiscal Year & Page Number Citations
```
