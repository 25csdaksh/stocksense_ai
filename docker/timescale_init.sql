-- ==============================================================================
-- MARKETMIND AI — TimescaleDB & PostgreSQL Schema Initialization
-- ==============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- 1. Assets Table
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(16) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    asset_type VARCHAR(50) DEFAULT 'EQUITY',
    market_cap NUMERIC(20, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    beta NUMERIC(6, 4),
    pe_ratio NUMERIC(10, 4),
    pb_ratio NUMERIC(10, 4),
    dividend_yield NUMERIC(6, 4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Market OHLCV Table (Timescale Hypertable)
CREATE TABLE IF NOT EXISTS market_ohlcv (
    time TIMESTAMPTZ NOT NULL,
    ticker VARCHAR(16) NOT NULL,
    open NUMERIC(14, 4) NOT NULL,
    high NUMERIC(14, 4) NOT NULL,
    low NUMERIC(14, 4) NOT NULL,
    close NUMERIC(14, 4) NOT NULL,
    adjusted_close NUMERIC(14, 4),
    volume NUMERIC(20, 2) NOT NULL,
    vwap NUMERIC(14, 4),
    is_synthetic BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (time, ticker)
);

-- Convert to Timescale Hypertable partitioned by 7 days
SELECT create_hypertable('market_ohlcv', 'time', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_ohlcv_ticker_time ON market_ohlcv (ticker, time DESC);

-- 3. Company Fundamentals Table
CREATE TABLE IF NOT EXISTS company_fundamentals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(16) REFERENCES assets(ticker) ON DELETE CASCADE,
    fiscal_period VARCHAR(20) NOT NULL,
    period_end_date DATE NOT NULL,
    revenue NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    free_cash_flow NUMERIC(20, 2),
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    pe_ratio NUMERIC(10, 4),
    pb_ratio NUMERIC(10, 4),
    debt_to_equity NUMERIC(10, 4),
    roe NUMERIC(10, 4),
    roa NUMERIC(10, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, fiscal_period)
);

-- 4. Anomaly Detection Table
CREATE TABLE IF NOT EXISTS detected_anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    ticker VARCHAR(16) REFERENCES assets(ticker) ON DELETE CASCADE,
    anomaly_type VARCHAR(50) NOT NULL,
    severity_score NUMERIC(5, 4) NOT NULL,
    z_score NUMERIC(8, 4),
    isolation_forest_score NUMERIC(8, 4),
    summary TEXT NOT NULL,
    context_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Scenario Simulation Runs
CREATE TABLE IF NOT EXISTS scenario_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    scenario_type VARCHAR(50) NOT NULL,
    target_tickers JSONB NOT NULL,
    parameters JSONB NOT NULL,
    results_summary JSONB NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed Initial Asset Metadata
INSERT INTO assets (ticker, name, sector, industry, asset_type, market_cap, pe_ratio, beta)
VALUES 
    ('AAPL', 'Apple Inc.', 'Information Technology', 'Consumer Electronics', 'EQUITY', 3450000000000, 33.5, 1.12),
    ('MSFT', 'Microsoft Corporation', 'Information Technology', 'Software - Infrastructure', 'EQUITY', 3200000000000, 35.8, 0.95),
    ('NVDA', 'NVIDIA Corporation', 'Information Technology', 'Semiconductors', 'EQUITY', 3100000000000, 52.4, 1.68),
    ('GOOGL', 'Alphabet Inc.', 'Communication Services', 'Internet Content & Information', 'EQUITY', 2150000000000, 24.2, 1.05),
    ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 'Internet Retail', 'EQUITY', 1980000000000, 42.1, 1.25),
    ('TSLA', 'Tesla Inc.', 'Consumer Discretionary', 'Auto Manufacturers', 'EQUITY', 780000000000, 68.3, 2.15),
    ('JPM', 'JPMorgan Chase & Co.', 'Financials', 'Banks - Diversified', 'EQUITY', 620000000000, 12.1, 1.08),
    ('SPY', 'SPDR S&P 500 ETF Trust', 'Index', 'Large Cap Blend', 'ETF', 540000000000, 27.8, 1.00),
    ('QQQ', 'Invesco QQQ Trust', 'Index', 'Large Cap Growth', 'ETF', 280000000000, 31.2, 1.18)
ON CONFLICT (ticker) DO NOTHING;
