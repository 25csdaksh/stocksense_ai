"""
MarketMind AI — Development Seed System.
Populates initial development universe (Sectors, Companies, Stocks, OHLCV, Fundamentals, News, SEC Filings, Portfolios).
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.session import engine, init_db, AsyncSessionLocal
from app.db.models import (
    User, Sector, Company, Stock, StockOHLCV, MarketIndex,
    Fundamental, FinancialStatement, News, Portfolio, Position,
    Watchlist, ResearchDocument, ResearchChunk
)
from app.core.security import hash_password
from app.utils.constants import SUPPORTED_UNIVERSE, DEFAULT_INDICES
from app.rag.retrieval import PRELOADED_SEC_CORPUS
from app.db.vector import vector_repository


async def seed_database(custom_engine=None):
    active_engine = custom_engine or engine
    print(f"[SEED] Initializing database schema on {active_engine.url}...")
    await init_db(active_engine)

    session_maker = async_sessionmaker(bind=active_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        print("[SEED] Seeding admin user...")
        admin = User(
            id="usr_dev_admin_001",
            username="admin",
            email="admin@marketmind.ai",
            hashed_password=hash_password("marketmind123"),
            full_name="MarketMind Quantitative Lead",
            is_active=True,
            is_superuser=True
        )
        session.add(admin)
        await session.flush()

        print("[SEED] Seeding sectors...")
        sectors_data = [
            {"name": "Information Technology", "code": "TECH", "perf": 1.42, "mom": 88.5, "weight": 0.31},
            {"name": "Communication Services", "code": "COMM", "perf": 0.85, "mom": 74.2, "weight": 0.09},
            {"name": "Consumer Discretionary", "code": "DISC", "perf": 0.62, "mom": 68.0, "weight": 0.10},
            {"name": "Financials", "code": "FIN", "perf": 0.34, "mom": 62.1, "weight": 0.13},
            {"name": "Health Care", "code": "HLTH", "perf": -0.18, "mom": 45.3, "weight": 0.12},
            {"name": "Energy", "code": "ENRG", "perf": -0.85, "mom": 31.0, "weight": 0.04},
            {"name": "Index ETF", "code": "ETF", "perf": 0.50, "mom": 60.0, "weight": 0.21},
        ]
        sector_map = {}
        for s in sectors_data:
            sec = Sector(
                name=s["name"],
                code=s["code"],
                performance_pct=s["perf"],
                momentum_score=s["mom"],
                market_cap_weight=s["weight"]
            )
            session.add(sec)
            await session.flush()
            sector_map[s["name"]] = sec.id

        print("[SEED] Seeding market indices...")
        for idx in DEFAULT_INDICES:
            m_idx = MarketIndex(
                symbol=idx["symbol"],
                name=idx["name"],
                price=idx["price"],
                change=idx["change"],
                change_pct=idx["change_pct"],
                timestamp=datetime.now(timezone.utc)
            )
            session.add(m_idx)
        await session.flush()

        print("[SEED] Seeding companies, stocks, OHLCVs, and fundamentals...")
        np.random.seed(42)

        for sym, meta in SUPPORTED_UNIVERSE.items():
            sec_id = sector_map.get(meta["sector"], sector_map["Information Technology"])
            comp = Company(
                name=meta["name"],
                ticker=sym,
                sector_id=sec_id,
                description=f"{meta['name']} is a leading global constituent in the {meta['sector']} sector.",
                country="US",
                website=f"https://www.{sym.lower()}.com"
            )
            session.add(comp)
            await session.flush()

            stk = Stock(
                company_id=comp.id,
                ticker=sym,
                exchange="NASDAQ" if sym != "JPM" and sym != "SPY" and sym != "QQQ" else "NYSE",
                asset_class="EQUITY" if not sym.endswith("Y") and not sym.endswith("Q") else "ETF",
                beta=meta.get("beta", 1.0),
                pe_ratio=meta.get("pe"),
                pb_ratio=meta.get("pb"),
                dividend_yield=meta.get("dividend_yield"),
                market_cap=meta.get("market_cap"),
                week_52_high=round(meta["base_price"] * 1.25, 2),
                week_52_low=round(meta["base_price"] * 0.78, 2)
            )
            session.add(stk)
            await session.flush()

            # Seed 120 days of historical OHLCV bars
            p = meta["base_price"] * 0.85
            base_date = datetime.now(timezone.utc) - timedelta(days=120)
            for d in range(120):
                bar_time = base_date + timedelta(days=d)
                p_change = np.random.normal(0.0008, 0.015)
                p_open = p
                p_close = p * (1.0 + p_change)
                p_high = max(p_open, p_close) * (1.0 + abs(np.random.normal(0, 0.006)))
                p_low = min(p_open, p_close) * (1.0 - abs(np.random.normal(0, 0.006)))
                p_vol = float(np.random.uniform(20000000, 60000000))
                p = p_close

                bar = StockOHLCV(
                    stock_id=stk.id,
                    ticker=sym,
                    timestamp=bar_time,
                    open=round(float(p_open), 2),
                    high=round(float(p_high), 2),
                    low=round(float(p_low), 2),
                    close=round(float(p_close), 2),
                    adjusted_close=round(float(p_close), 2),
                    volume=p_vol,
                    interval="1d"
                )
                session.add(bar)

            # Seed Fundamentals
            funda = Fundamental(
                company_id=comp.id,
                fiscal_year=2024,
                fiscal_quarter=4,
                pe_ratio=meta.get("pe", 28.0),
                forward_pe=round(meta.get("pe", 28.0) * 0.88, 1),
                pb_ratio=meta.get("pb", 6.0),
                ev_ebitda=22.5,
                fcf_yield_pct=3.8,
                gross_margin_pct=45.2,
                operating_margin_pct=28.4,
                net_margin_pct=23.1,
                roe_pct=32.4,
                roa_pct=14.8,
                current_ratio=1.45,
                debt_to_equity=0.62,
                interest_coverage_ratio=18.5,
                altman_z_score=4.82,
                health_score="HEALTHY"
            )
            session.add(funda)

            # Seed Financial Statements
            stmt = FinancialStatement(
                company_id=comp.id,
                statement_type="income",
                fiscal_year=2024,
                fiscal_period="FY",
                reported_date=datetime.now(timezone.utc),
                raw_data={
                    "total_revenue": 383285000000,
                    "gross_profit": 170782000000,
                    "operating_income": 114301000000,
                    "net_income": 96995000000,
                    "ebitda": 125820000000
                }
            )
            session.add(stmt)

        print("[SEED] Seeding financial news...")
        news_items = [
            ("NVIDIA Expands Blackwell Ultra GPU Infrastructure to Tier-1 Cloud Datacenters", "NVDA", "BULLISH", 0.88),
            ("Apple Services Division Records Strong Growth in Active Installed Base", "AAPL", "BULLISH", 0.65),
            ("Microsoft Expands Azure AI Enterprise Deployments with Copilot Studio", "MSFT", "BULLISH", 0.72),
            ("Federal Reserve Signals Cautious Rate Path Amid Resilient Labor Market", "SPY", "NEUTRAL", 0.10),
            ("Tesla Advances Autonomous FSD Hardware Architecture Deployment", "TSLA", "BULLISH", 0.55),
        ]
        for title, sym, sent, score in news_items:
            nw = News(
                ticker=sym,
                title=title,
                summary=f"{title}. Institutional order flow and options volume indicated heightened positioning.",
                source="MarketMind Wire",
                url=f"https://marketmind.ai/news/{sym.lower()}",
                published_at=datetime.now(timezone.utc),
                sentiment_label=sent,
                sentiment_score=score,
                impact_score=0.75
            )
            session.add(nw)

        print("[SEED] Seeding admin portfolio & watchlist...")
        port = Portfolio(
            id="port_dev_admin_001",
            user_id=admin.id,
            name="Primary Growth & Tech Portfolio",
            description="High-duration tech and semiconductor equity allocations",
            cash_balance=45000.0,
            total_value=125800.0,
            weighted_beta=1.28,
            daily_var_95_pct=2.45
        )
        session.add(port)
        await session.flush()

        positions = [
            ("AAPL", 50.0, 175.0, "Information Technology", 1.12),
            ("NVDA", 25.0, 420.0, "Information Technology", 1.68),
            ("MSFT", 30.0, 380.0, "Information Technology", 0.95),
            ("JPM", 40.0, 185.0, "Financials", 1.08),
        ]
        for sym, shs, cost, sec, beta in positions:
            pos = Position(
                portfolio_id=port.id,
                ticker=sym,
                shares=shs,
                avg_cost=cost,
                sector=sec,
                beta=beta
            )
            session.add(pos)

        # Watchlist
        session.add(Watchlist(user_id=admin.id, ticker="TSLA", target_price=280.0, notes="EV margin watch"))
        session.add(Watchlist(user_id=admin.id, ticker="GOOGL", target_price=190.0, notes="Gemini server watch"))

        print("[SEED] Seeding SEC 10-K filings into relational DB & Qdrant vector index...")
        for doc in PRELOADED_SEC_CORPUS:
            rdoc = ResearchDocument(
                ticker=doc["ticker"],
                title=doc["title"],
                filing_type=doc["filing_type"],
                fiscal_year=doc["fiscal_year"],
                total_chunks=1
            )
            session.add(rdoc)
            await session.flush()

            rchunk = ResearchChunk(
                document_id=rdoc.id,
                chunk_index=0,
                section=doc["section"],
                page_number=doc["page_number"],
                content=doc["content"],
                vector_id=doc["id"]
            )
            session.add(rchunk)

        # Index vectors in Qdrant / in-memory VectorRepository
        vector_repository.initialize()
        vector_repository.upsert_chunks(PRELOADED_SEC_CORPUS)

        await session.commit()
        print("[SEED] SUCCESS: Database seeding complete with 9 universe assets, 120-day OHLCVs, fundamentals, news, admin portfolio, and SEC vectors.")


if __name__ == "__main__":
    test_db = create_async_engine("sqlite+aiosqlite:///dev_marketmind.db", echo=False)
    asyncio.run(seed_database(custom_engine=test_db))
