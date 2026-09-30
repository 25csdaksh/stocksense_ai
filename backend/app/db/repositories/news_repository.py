"""
Financial News Articles & Sentiment Repository.
Phase 6.7: Complete async repository supporting upserts, hash deduplication,
filtered timeline queries, and sector aggregations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from app.db.repositories.base import BaseRepository
from app.db.models.news import News
from app.db.base import utc_now
from app.providers.news.models import NewsArticleData


class NewsRepository(BaseRepository[News]):

    def __init__(self, session: AsyncSession):
        super().__init__(News, session)

    async def get_by_ticker(
        self,
        ticker: str,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[News]:
        filters = [News.ticker == ticker.strip().upper()]
        if from_date:
            filters.append(News.published_at >= from_date)
        if to_date:
            filters.append(News.published_at <= to_date)

        stmt = (
            select(News)
            .where(and_(*filters))
            .order_by(News.published_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_sector(self, sector: str, limit: int = 10) -> List[News]:
        stmt = (
            select(News)
            .where(News.sector.ilike(f"%{sector}%"))
            .order_by(News.published_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_market_feed(
        self,
        limit: int = 20,
        category: Optional[str] = None,
        event_type: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> List[News]:
        filters = []
        if category and category.upper() != "ALL":
            filters.append(News.category == category.upper())
        if event_type and event_type.upper() != "ALL":
            filters.append(News.event_type == event_type.upper())
        if sentiment and sentiment.upper() != "ALL":
            filters.append(or_(News.sentiment_label == sentiment.upper(), News.sentiment_label == sentiment))

        stmt = select(News)
        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(News.published_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_content_hash(self, content_hash: str) -> Optional[News]:
        if not content_hash:
            return None
        stmt = select(News).where(News.content_hash == content_hash).limit(1)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_url(self, url: str) -> Optional[News]:
        if not url:
            return None
        stmt = select(News).where(News.url == url).limit(1)
        res = await self.session.execute(stmt)
        return res.scalars().first()

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
        published_at: Optional[datetime] = None,
        category: str = "MARKET",
        event_type: str = "OTHER",
        sector: Optional[str] = None,
        content_hash: Optional[str] = None,
        data_source: str = "DEMO",
        data_status: str = "DEMO"
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
            published_at=published_at or utc_now(),
            category=category,
            event_type=event_type,
            sector=sector,
            content_hash=content_hash,
            data_source=data_source,
            data_status=data_status
        )

    async def upsert_article(self, article: NewsArticleData) -> News:
        """Upserts a normalized NewsArticleData, avoiding duplicate records."""
        existing = None
        if article.content_hash:
            existing = await self.get_by_content_hash(article.content_hash)
        if not existing and article.url:
            existing = await self.get_by_url(article.url)

        if existing:
            # Update existing article metadata if needed
            existing.sentiment_score = article.sentiment_score
            existing.sentiment_label = article.sentiment_label
            existing.impact_score = article.impact_score
            existing.category = article.category.value
            existing.event_type = article.event_type.value
            if article.sector:
                existing.sector = article.sector
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        # Parse published_at
        pub_dt = utc_now()
        if article.published_at:
            try:
                # Try ISO format
                clean_pub = article.published_at.replace("Z", "+00:00")
                if "UTC" in clean_pub:
                    clean_pub = clean_pub.replace(" UTC", "")
                    pub_dt = datetime.strptime(clean_pub, "%Y-%m-%d %H:%M:%S")
                else:
                    pub_dt = datetime.fromisoformat(clean_pub)
            except Exception:
                pub_dt = utc_now()

        return await self.create_article(
            title=article.headline or article.title,
            summary=article.summary,
            source=article.source,
            ticker=article.ticker,
            url=article.url,
            sentiment_label=article.sentiment_label,
            sentiment_score=article.sentiment_score,
            impact_score=article.impact_score,
            published_at=pub_dt,
            category=article.category.value,
            event_type=article.event_type.value,
            sector=article.sector,
            content_hash=article.content_hash,
            data_source=article.data_source.value,
            data_status=article.data_status.value
        )
