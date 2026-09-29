"""
Integration Tests: All 11 SQLAlchemy 2.0 Repositories Operations.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
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


@pytest.mark.asyncio
async def test_all_11_repositories(db_session: AsyncSession):
    # 1. UserRepository
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("repo_tester", "tester@marketmind.ai", "pass123")
    assert user.id is not None

    # 2. CompanyRepository
    comp_repo = CompanyRepository(db_session)
    sec = await comp_repo.create_sector("Tech", "TECH", 1.2)
    comp = await comp_repo.create(name="Apple", ticker="AAPL", sector_id=sec.id)
    assert comp.id is not None

    # 3. StockRepository
    stock_repo = StockRepository(db_session)
    stk = await stock_repo.upsert_stock("AAPL", company_id=comp.id, beta=1.12)
    assert stk.ticker == "AAPL"

    # 4. MarketDataRepository
    mkt_repo = MarketDataRepository(db_session)
    await mkt_repo.insert_ohlcv_batch([{
        "stock_id": stk.id,
        "ticker": "AAPL",
        "timestamp": datetime.now(timezone.utc),
        "open": 220.0,
        "high": 225.0,
        "low": 219.0,
        "close": 224.0,
        "volume": 100000.0,
        "interval": "1d"
    }])
    bars = await mkt_repo.get_ohlcv_range("AAPL", limit=5)
    assert len(bars) == 1

    # 5. FundamentalRepository
    funda_repo = FundamentalRepository(db_session)
    funda = await funda_repo.create(company_id=comp.id, fiscal_year=2024, pe_ratio=32.0, health_score="HEALTHY")
    assert funda.id is not None

    # 6. NewsRepository
    news_repo = NewsRepository(db_session)
    nw = await news_repo.create_article(
        title="Apple Services Surge",
        summary="Services gross margin expanded.",
        source="Market Wire",
        ticker="AAPL"
    )
    assert nw.id is not None

    # 7. PortfolioRepository
    port_repo = PortfolioRepository(db_session)
    port = await port_repo.get_or_create_default(user.id)
    tx = await port_repo.add_transaction(port.id, "AAPL", shares=10.0, price=200.0, tx_type="BUY")
    assert tx["status"] == "SUCCESS"

    # 8. WatchlistRepository
    wl_repo = WatchlistRepository(db_session)
    wl = await wl_repo.add_item(user.id, "AAPL", target_price=250.0)
    assert wl.ticker == "AAPL"

    # 9. ScenarioRepository
    scen_repo = ScenarioRepository(db_session)
    scen = await scen_repo.save_report("AAPL", "MONTE_CARLO", {"days": 90}, {"var95": -12.5})
    assert scen.id is not None

    # 10. ResearchRepository
    r_repo = ResearchRepository(db_session)
    doc = await r_repo.create_document_with_chunks("AAPL", "10-K FY2024", "10-K", 2024, [{"section": "Risk", "content": "Supply chain"}])
    assert doc.id is not None

    # 11. AIQueryRepository
    ai_repo = AIQueryRepository(db_session)
    chat = await ai_repo.get_or_create_session(user_id=user.id, title="Test Session")
    q_log = await ai_repo.log_query(
        session_id=chat.id,
        user_id=user.id,
        query_text="AAPL risk?",
        intent="RAG",
        ticker_focus="AAPL",
        thought_steps=[],
        tool_calls=[],
        answer="Supply chain",
        citations=[],
        ui_widgets=[]
    )
    assert q_log.id is not None
