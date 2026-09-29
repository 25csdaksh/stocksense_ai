"""
SQLAlchemy 2.0 Repositories Unit Tests.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.repositories import (
    UserRepository,
    CompanyRepository,
    StockRepository,
    MarketDataRepository,
    FundamentalRepository,
    NewsRepository,
    PortfolioRepository,
    WatchlistRepository,
    ScenarioRepository,
    ResearchRepository,
    AIQueryRepository
)


@pytest_asyncio.fixture(loop_scope="function")
async def repo_session():
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
async def test_user_repository_crud(repo_session: AsyncSession):
    repo = UserRepository(repo_session)
    user = await repo.create_user(
        username="lead_quant",
        email="quant@marketmind.ai",
        password="secret_password_123",
        full_name="Lead Quantitative Analyst"
    )
    assert user.id is not None
    assert user.username == "lead_quant"

    by_uname = await repo.get_by_username("lead_quant")
    assert by_uname is not None
    assert by_uname.email == "quant@marketmind.ai"

    by_email = await repo.get_by_email("quant@marketmind.ai")
    assert by_email is not None
    assert by_email.id == user.id


@pytest.mark.asyncio
async def test_company_and_stock_repository(repo_session: AsyncSession):
    comp_repo = CompanyRepository(repo_session)
    stock_repo = StockRepository(repo_session)

    sector = await comp_repo.create_sector(name="Information Technology", code="TECH", performance_pct=2.1)
    assert sector.id is not None

    comp = await comp_repo.create(name="Apple Inc.", ticker="AAPL", sector_id=sector.id)
    assert comp.id is not None

    stk = await stock_repo.upsert_stock(
        ticker="AAPL",
        company_id=comp.id,
        exchange="NASDAQ",
        beta=1.12,
        pe_ratio=33.8
    )
    assert stk.id is not None
    assert stk.ticker == "AAPL"

    stk_lookup = await stock_repo.get_by_ticker("AAPL")
    assert stk_lookup is not None
    assert stk_lookup.company.name == "Apple Inc."


@pytest.mark.asyncio
async def test_market_data_repository(repo_session: AsyncSession):
    comp_repo = CompanyRepository(repo_session)
    stock_repo = StockRepository(repo_session)
    mkt_repo = MarketDataRepository(repo_session)

    sec = await comp_repo.create_sector(name="Semiconductors", code="SEMI")
    comp = await comp_repo.create(name="NVIDIA", ticker="NVDA", sector_id=sec.id)
    stk = await stock_repo.upsert_stock(ticker="NVDA", company_id=comp.id, beta=1.68)

    bars_data = [
        {
            "stock_id": stk.id,
            "ticker": "NVDA",
            "timestamp": datetime.now(timezone.utc),
            "open": 120.0,
            "high": 125.0,
            "low": 119.5,
            "close": 124.5,
            "adjusted_close": 124.5,
            "volume": 35000000.0,
            "interval": "1d"
        }
    ]
    inserted = await mkt_repo.insert_ohlcv_batch(bars_data)
    assert inserted == 1

    bars = await mkt_repo.get_ohlcv_range("NVDA", limit=10)
    assert len(bars) == 1
    assert bars[0].close == 124.5

    # Index upsert
    idx = await mkt_repo.upsert_index("^GSPC", "S&P 500", price=5750.0, change=25.0, change_pct=0.45)
    assert idx.symbol == "^GSPC"


@pytest.mark.asyncio
async def test_portfolio_and_watchlist_repository(repo_session: AsyncSession):
    user_repo = UserRepository(repo_session)
    user = await user_repo.create_user("investor_repo", "inv_repo@marketmind.ai", "pw123")

    port_repo = PortfolioRepository(repo_session)
    port = await port_repo.get_or_create_default(user.id)
    assert port.id is not None

    tx = await port_repo.add_transaction(
        portfolio_id=port.id,
        ticker="MSFT",
        shares=15.0,
        price=380.0,
        tx_type="BUY"
    )
    assert tx["status"] == "SUCCESS"

    positions = await port_repo.get_positions(port.id)
    assert len(positions) == 1
    assert positions[0].ticker == "MSFT"
    assert positions[0].shares == 15.0

    wl_repo = WatchlistRepository(repo_session)
    wl_item = await wl_repo.add_item(user.id, "GOOGL", target_price=190.0, notes="Gemini watch")
    assert wl_item.ticker == "GOOGL"

    user_wl = await wl_repo.get_by_user(user.id)
    assert len(user_wl) == 1

    removed = await wl_repo.remove_item(user.id, "GOOGL")
    assert removed is True


@pytest.mark.asyncio
async def test_research_and_ai_query_repository(repo_session: AsyncSession):
    user_repo = UserRepository(repo_session)
    user = await user_repo.create_user("ai_user", "ai_user@marketmind.ai", "pw123")

    r_repo = ResearchRepository(repo_session)
    doc = await r_repo.create_document_with_chunks(
        ticker="AAPL",
        title="Apple 10-K FY2024",
        filing_type="10-K",
        fiscal_year=2024,
        chunks=[
            {"section": "Item 1 Business", "page_number": 12, "content": "Services revenue reached $96B."}
        ]
    )
    assert doc.id is not None
    assert doc.total_chunks == 1

    ai_repo = AIQueryRepository(repo_session)
    chat = await ai_repo.get_or_create_session(user_id=user.id, title="Apple Revenue Deep Dive")
    assert chat.id is not None

    q_log = await ai_repo.log_query(
        session_id=chat.id,
        user_id=user.id,
        query_text="What was Apple's Services revenue?",
        intent="RAG_SEARCH",
        ticker_focus="AAPL",
        thought_steps=[{"step": 1, "agent": "rag", "message": "Searching Item 1"}],
        tool_calls=[{"tool": "sec_search"}],
        answer="Apple reported $96.2 billion in Services revenue for FY2024.",
        citations=[{"doc_id": doc.id}],
        ui_widgets=[],
        guardrail_passed=True
    )
    assert q_log.id is not None
    assert q_log.ticker_focus == "AAPL"
