"""
SQLAlchemy 2.0 ORM Models Unit Tests (Using Async In-Memory Test DB).
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.models import (
    User, Sector, Company, Stock, StockOHLCV, MarketIndex,
    Fundamental, FinancialStatement, News, Anomaly, ScenarioReport,
    Portfolio, Position, Transaction, Watchlist, ChatSession, AIQuery,
    ResearchDocument, ResearchChunk
)
from app.core.security import hash_password, verify_password


@pytest_asyncio.fixture(loop_scope="function")
async def test_session():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_user_and_auth_persistence(test_session: AsyncSession):
    user = User(
        username="quant_trader",
        email="trader@marketmind.ai",
        hashed_password=hash_password("secure_pass_2026"),
        full_name="Lead Quant Trader"
    )
    test_session.add(user)
    await test_session.commit()

    assert user.id is not None
    assert verify_password("secure_pass_2026", user.hashed_password)
    assert user.is_active is True
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_company_stock_and_ohlcv_models(test_session: AsyncSession):
    # Sector
    sector = Sector(name="Information Technology", code="TECH", performance_pct=1.5, momentum_score=85.0)
    test_session.add(sector)
    await test_session.flush()

    # Company
    comp = Company(name="Apple Inc.", ticker="AAPL", sector_id=sector.id, country="US")
    test_session.add(comp)
    await test_session.flush()

    # Stock
    stk = Stock(company_id=comp.id, ticker="AAPL", beta=1.12, pe_ratio=33.5, market_cap=3.4e12)
    test_session.add(stk)
    await test_session.flush()

    # StockOHLCV
    ohlcv = StockOHLCV(
        stock_id=stk.id,
        ticker="AAPL",
        timestamp=datetime.now(timezone.utc),
        open=225.0,
        high=228.0,
        low=224.5,
        close=227.5,
        adjusted_close=227.5,
        volume=45000000.0,
        interval="1d"
    )
    test_session.add(ohlcv)
    await test_session.commit()

    assert stk.id is not None
    assert ohlcv.id is not None
    assert ohlcv.close == 227.5


@pytest.mark.asyncio
async def test_portfolio_holdings_and_transactions(test_session: AsyncSession):
    user = User(username="investor1", email="inv1@marketmind.ai", hashed_password="pw")
    test_session.add(user)
    await test_session.flush()

    port = Portfolio(user_id=user.id, name="Growth Fund", total_value=50000.0)
    test_session.add(port)
    await test_session.flush()

    pos = Position(portfolio_id=port.id, ticker="NVDA", shares=20.0, avg_cost=400.0, beta=1.75)
    test_session.add(pos)

    tx = Transaction(portfolio_id=port.id, ticker="NVDA", shares=20.0, price=400.0, transaction_type="BUY")
    test_session.add(tx)

    wl = Watchlist(user_id=user.id, ticker="TSLA", target_price=275.0, notes="EV inflection point")
    test_session.add(wl)

    await test_session.commit()
    assert pos.shares == 20.0
    assert tx.transaction_type == "BUY"
    assert wl.ticker == "TSLA"


@pytest.mark.asyncio
async def test_fundamentals_news_and_scenarios(test_session: AsyncSession):
    sector = Sector(name="Financials", code="FIN")
    test_session.add(sector)
    await test_session.flush()

    comp = Company(name="JPMorgan Chase", ticker="JPM", sector_id=sector.id)
    test_session.add(comp)
    await test_session.flush()

    stk = Stock(company_id=comp.id, ticker="JPM", beta=1.05)
    test_session.add(stk)
    await test_session.flush()

    funda = Fundamental(company_id=comp.id, fiscal_year=2024, pe_ratio=12.5, roe_pct=17.2, health_score="HEALTHY")
    test_session.add(funda)

    nw = News(
        ticker="JPM",
        title="JPMorgan Reports Robust Net Interest Income",
        summary="Q4 net income exceeded consensus expectations.",
        source="Reuters",
        sentiment_label="BULLISH",
        sentiment_score=0.78
    )
    test_session.add(nw)

    scen = ScenarioReport(
        stock_id=stk.id,
        ticker="JPM",
        scenario_type="HISTORICAL_STRESS",
        parameters={"scenario": "GFC_2008"},
        results={"projected_drawdown_pct": -65.0}
    )
    test_session.add(scen)

    await test_session.commit()
    assert funda.health_score == "HEALTHY"
    assert nw.sentiment_label == "BULLISH"
    assert scen.scenario_type == "HISTORICAL_STRESS"


@pytest.mark.asyncio
async def test_ai_and_research_models(test_session: AsyncSession):
    user = User(username="analyst_ai", email="analyst@marketmind.ai", hashed_password="pw")
    test_session.add(user)
    await test_session.flush()

    chat = ChatSession(user_id=user.id, title="Tech Sector Valuation Analysis")
    test_session.add(chat)
    await test_session.flush()

    query = AIQuery(
        session_id=chat.id,
        user_id=user.id,
        query_text="Assess NVDA valuation sensitivity",
        intent="QUANT_SCENARIO",
        ticker_focus="NVDA",
        thought_steps=[{"step": 1, "agent": "supervisor", "message": "Routing to quant engine"}],
        tool_calls=[{"tool": "monte_carlo", "status": "COMPLETED"}],
        answer="NVDA expected terminal price is $135.20 with 95% VaR at -14.2%.",
        citations=[{"source": "SEC 10-K"}],
        ui_widgets=[{"widget_type": "FAN_CHART"}],
        guardrail_passed=True
    )
    test_session.add(query)

    rdoc = ResearchDocument(ticker="NVDA", title="NVIDIA 10-K FY2024", filing_type="10-K", fiscal_year=2024, total_chunks=1)
    test_session.add(rdoc)
    await test_session.flush()

    rchunk = ResearchChunk(
        document_id=rdoc.id,
        chunk_index=0,
        section="Item 1A Risk Factors",
        content="We rely on TSMC for semiconductor wafers.",
        vector_id="vec_nvda_001"
    )
    test_session.add(rchunk)

    await test_session.commit()
    assert query.guardrail_passed is True
    assert rchunk.vector_id == "vec_nvda_001"
