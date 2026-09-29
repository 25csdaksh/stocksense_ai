"""
Financial News Articles & Sentiment Repository.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.repositories.base import BaseRepository
from app.db.models.news import News
from app.db.base import utc_now


class NewsRepository(BaseRepository[News]):

    def __init__(self, session: AsyncSession):
        super().__init__(News, session)

    async def get_by_ticker(self, ticker: str, limit: int = 10) -> List[News]:
        stmt = (
            select(News)
            .where(News.ticker == ticker.strip().upper())
            .order_by(News.published_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_market_feed(self, limit: int = 20) -> List[News]:
        stmt = select(News).order_by(News.published_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_article(
        self,
        title: str,
        summary: str,
        source: str,
        ticker: Optional[str] = None,
        company_id: Optional[str] = None,
        url: Optional[str] = None,
        sentiment_label: str = "NEUTRAL",
        sentiment_score: float = 0.0,
        impact_score: float = 0.5,
        published_at: Optional[datetime] = None
    ) -> News:
        return await self.create(
            title=title,
            summary=summary,
            source=source,
            ticker=ticker.upper() if ticker else None,
            company_id=company_id,
            url=url,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            impact_score=impact_score,
            published_at=published_at or utc_now()
        )
