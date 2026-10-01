"""
MarketMind AI — User Research Memory & Portfolio Alert Repository.
Phase 6.10: Database operations for user-isolated research memory, alert rules, and audit events.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_, delete, update
from app.db.models.research_memory import (
    UserResearchMemory,
    PortfolioAlert,
    AlertRule,
    AlertEvent,
)


class ResearchMemoryRepository:
    """Provides user-isolated persistence and querying for research memories and portfolio alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # Research Memory Operations
    # =========================================================================

    async def save_memory(
        self,
        user_id: str,
        research_id: str,
        query: str,
        symbols: List[str],
        intent: str,
        execution_depth: str = "STANDARD",
        report_summary: Optional[str] = None,
        evidence_count: int = 0,
        confidence_level: str = "MEDIUM",
        confidence_rationale: Optional[str] = None,
        provenance_summary: Optional[Dict[str, Any]] = None,
        key_metrics: Optional[Dict[str, Any]] = None,
        cited_sources: Optional[List[Dict[str, Any]]] = None,
        data_status: str = "DEMO",
        research_version: str = "6.10",
    ) -> UserResearchMemory:
        """Stores a new research memory entry strictly isolated to the user."""
        memory = UserResearchMemory(
            user_id=user_id,
            research_id=research_id,
            query=query,
            symbols=symbols,
            intent=intent,
            execution_depth=execution_depth,
            report_summary=report_summary,
            evidence_count=evidence_count,
            confidence_level=confidence_level,
            confidence_rationale=confidence_rationale,
            provenance_summary=provenance_summary or {},
            key_metrics=key_metrics or {},
            cited_sources=cited_sources or [],
            data_status=data_status,
            research_version=research_version,
        )
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserResearchMemory]:
        """Retrieves recent research memories for the specified user in reverse chronological order."""
        stmt = (
            select(UserResearchMemory)
            .where(UserResearchMemory.user_id == user_id)
            .order_by(desc(UserResearchMemory.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_memory_by_id(
        self,
        user_id: str,
        research_id: str
    ) -> Optional[UserResearchMemory]:
        """Retrieves a specific research memory ensuring user ownership isolation (IDOR protection)."""
        stmt = select(UserResearchMemory).where(
            and_(
                UserResearchMemory.user_id == user_id,
                or_(
                    UserResearchMemory.research_id == research_id,
                    UserResearchMemory.id == research_id
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_memory_for_symbol(
        self,
        user_id: str,
        symbol: str
    ) -> Optional[UserResearchMemory]:
        """Fetches the most recent research memory involving a specific ticker."""
        stmt = (
            select(UserResearchMemory)
            .where(UserResearchMemory.user_id == user_id)
            .order_by(desc(UserResearchMemory.created_at))
            .limit(50)
        )
        res = await self.db.execute(stmt)
        memories = res.scalars().all()
        for mem in memories:
            syms = mem.symbols or []
            if symbol.upper() in [s.upper() for s in syms]:
                return mem
        return None

    # =========================================================================
    # Portfolio Alert & Rule Operations
    # =========================================================================

    async def create_alert(
        self,
        user_id: str,
        title: str,
        message: str,
        alert_type: str = "PRICE_MOVE",
        symbol: Optional[str] = None,
        portfolio_id: Optional[str] = None,
        severity: str = "INFO",
        trigger_metric: Optional[str] = None,
        trigger_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        provenance: str = "DEMO"
    ) -> PortfolioAlert:
        """Persists a new factual portfolio or watchlist alert."""
        alert = PortfolioAlert(
            user_id=user_id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            alert_type=alert_type,
            title=title,
            message=message,
            severity=severity,
            trigger_metric=trigger_metric,
            trigger_value=trigger_value,
            threshold_value=threshold_value,
            provenance=provenance,
            is_read=False
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_user_alerts(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[PortfolioAlert]:
        """Fetches alerts for the authenticated user."""
        conditions = [PortfolioAlert.user_id == user_id]
        if unread_only:
            conditions.append(PortfolioAlert.is_read == False)

        stmt = (
            select(PortfolioAlert)
            .where(and_(*conditions))
            .order_by(desc(PortfolioAlert.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def mark_alert_read(self, user_id: str, alert_id: str) -> bool:
        """Marks an alert as read ensuring user ownership."""
        stmt = (
            update(PortfolioAlert)
            .where(and_(PortfolioAlert.id == alert_id, PortfolioAlert.user_id == user_id))
            .values(is_read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def create_alert_rule(
        self,
        user_id: str,
        rule_type: str,
        threshold: float,
        symbol: Optional[str] = None,
        portfolio_id: Optional[str] = None,
        timeframe: str = "1d"
    ) -> AlertRule:
        """Creates a new threshold alert rule for a user."""
        rule = AlertRule(
            user_id=user_id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            rule_type=rule_type,
            threshold=threshold,
            timeframe=timeframe,
            is_active=True
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_user_alert_rules(
        self,
        user_id: str,
        active_only: bool = True
    ) -> List[AlertRule]:
        """Retrieves alert rules owned by the user."""
        conditions = [AlertRule.user_id == user_id]
        if active_only:
            conditions.append(AlertRule.is_active == True)
        stmt = select(AlertRule).where(and_(*conditions)).order_by(desc(AlertRule.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def delete_alert_rule(self, user_id: str, rule_id: str) -> bool:
        """Deletes an alert rule with ownership validation."""
        stmt = delete(AlertRule).where(and_(AlertRule.id == rule_id, AlertRule.user_id == user_id))
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0
