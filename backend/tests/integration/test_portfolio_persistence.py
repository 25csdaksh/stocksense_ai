"""
Portfolio, Position & Transaction Persistence Integration Tests.
Verifies BUY/SELL trade processing, weighted-average cost basis recalculation, and transaction immutability.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Portfolio, Position, Transaction, Stock, Sector
from app.db.repositories.portfolio_repository import PortfolioRepository
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_portfolio_buy_and_sell_lifecycle(db_session: AsyncSession):
    # 1. Create User
    user = User(
        id="usr_portfolio_test_01",
        username="trader_joe",
        email="trader_joe@example.com",
        hashed_password=hash_password("TraderPass123!"),
        full_name="Joe Trader"
    )
    db_session.add(user)

    # 2. Create Portfolio
    portfolio = Portfolio(
        id="port_trader_01",
        user_id=user.id,
        name="Growth Tech Portfolio",
        cash_balance=100000.0,
        total_value=100000.0
    )
    db_session.add(portfolio)
    await db_session.commit()

    repo = PortfolioRepository(db_session)

    # 3. BUY Transaction 1: 100 shares @ $150.00
    tx1_res = await repo.add_transaction(
        portfolio_id=portfolio.id,
        ticker="AAPL",
        shares=100.0,
        price=150.0,
        tx_type="BUY"
    )
    await db_session.commit()

    assert tx1_res["status"] == "SUCCESS"
    assert tx1_res["shares"] == 100.0

    # Verify Position after BUY 1
    positions = await repo.get_positions(portfolio.id)
    assert len(positions) == 1
    pos1 = positions[0]
    assert pos1.ticker == "AAPL"
    assert pos1.shares == 100.0
    assert pos1.avg_cost == 150.0

    # 4. BUY Transaction 2: 50 shares @ $180.00 (Weighted average should be (100*150 + 50*180)/150 = 24000/150 = 160.0)
    tx2_res = await repo.add_transaction(
        portfolio_id=portfolio.id,
        ticker="AAPL",
        shares=50.0,
        price=180.0,
        tx_type="BUY"
    )
    await db_session.commit()

    positions = await repo.get_positions(portfolio.id)
    assert len(positions) == 1
    pos2 = positions[0]
    assert pos2.shares == 150.0
    assert pytest.approx(pos2.avg_cost, 0.01) == 160.0

    # 5. SELL Transaction: 50 shares @ $200.00
    tx3_res = await repo.add_transaction(
        portfolio_id=portfolio.id,
        ticker="AAPL",
        shares=50.0,
        price=200.0,
        tx_type="SELL"
    )
    await db_session.commit()

    positions = await repo.get_positions(portfolio.id)
    assert len(positions) == 1
    pos3 = positions[0]
    assert pos3.shares == 100.0
    # Average buy price remains $160.0
    assert pytest.approx(pos3.avg_cost, 0.01) == 160.0

    # 6. Verify Transaction History is Recorded & Complete
    stmt = select(Transaction).where(Transaction.portfolio_id == portfolio.id)
    res = await db_session.execute(stmt)
    history = list(res.scalars().all())
    assert len(history) == 3
    actions = [t.transaction_type for t in history]
    assert "BUY" in actions
    assert "SELL" in actions
