"""
User Watchlist Repository.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.repositories.base import BaseRepository
from app.db.models.portfolio import Watchlist
from app.db.base import utc_now


class WatchlistRepository(BaseRepository[Watchlist]):

    def __init__(self, session: AsyncSession):
        super().__init__(Watchlist, session)

    async def get_by_user(self, user_id: str) -> List[Watchlist]:
        stmt = select(Watchlist).where(Watchlist.user_id == user_id).order_by(Watchlist.added_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_item(
        self,
        user_id: str,
        ticker: str,
        target_price: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Watchlist:
        sym = ticker.strip().upper()
        stmt = select(Watchlist).where(Watchlist.user_id == user_id, Watchlist.ticker == sym)
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.target_price = target_price
            existing.notes = notes
            existing.added_at = utc_now()
            await self.session.flush()
            return existing
        else:
            return await self.create(
                user_id=user_id,
                ticker=sym,
                target_price=target_price,
                notes=notes,
                added_at=utc_now()
            )

    async def remove_item(self, user_id: str, ticker: str) -> bool:
        stmt = delete(Watchlist).where(Watchlist.user_id == user_id, Watchlist.ticker == ticker.strip().upper())
        res = await self.session.execute(stmt)
        return res.rowcount > 0
