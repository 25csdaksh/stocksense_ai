"""
MarketMind AI — Portfolio Factual Alert Engine.
Phase 6.10: User-scoped rule evaluation, threshold monitoring, and factual alert generation.
Strictly avoids buy/sell directives, providing only objective threshold notifications.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.portfolio.models import (
    UserResearchContext,
    PortfolioAlertRuleModel,
    PortfolioAlertEventModel,
    AlertRuleType,
    AlertSeverity,
)
from app.db.repositories.research_memory_repository import ResearchMemoryRepository
from app.core.logging import logger


class PortfolioAlertEngine:
    """Evaluates threshold rules against user portfolio telemetry and emits factual notifications."""

    async def evaluate_rules(
        self,
        user_id: str,
        user_context: UserResearchContext,
        db: Optional[AsyncSession] = None
    ) -> List[PortfolioAlertEventModel]:
        """Evaluates configured user rules and returns generated alert events."""
        alerts_emitted: List[PortfolioAlertEventModel] = []

        # 1. Fetch active user rules from DB if available
        rules = []
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_rules = await repo.get_user_alert_rules(user_id=user_id, active_only=True)
                rules = [
                    PortfolioAlertRuleModel(
                        rule_id=r.id,
                        user_id=r.user_id,
                        portfolio_id=r.portfolio_id,
                        symbol=r.symbol,
                        rule_type=r.rule_type,
                        threshold=r.threshold,
                        timeframe=r.timeframe,
                        is_active=r.is_active,
                        created_at=r.created_at.isoformat()
                    )
                    for r in db_rules
                ]
            except Exception as ex:
                logger.warning(f"Error reading alert rules: {ex}")

        # Default standard baseline rules if user has no custom rules configured
        if not rules:
            rules = [
                PortfolioAlertRuleModel(
                    rule_id=f"rule_def_weight_{user_id}",
                    user_id=user_id,
                    rule_type=AlertRuleType.WEIGHT_THRESHOLD.value,
                    threshold=25.0,
                    timeframe="1d",
                    is_active=True,
                    created_at=datetime.now(timezone.utc).isoformat()
                ),
                PortfolioAlertRuleModel(
                    rule_id=f"rule_def_vol_{user_id}",
                    user_id=user_id,
                    rule_type=AlertRuleType.VOLATILITY_THRESHOLD.value,
                    threshold=30.0,
                    timeframe="1d",
                    is_active=True,
                    created_at=datetime.now(timezone.utc).isoformat()
                )
            ]

        holdings = user_context.portfolio.holdings

        for rule in rules:
            # Rule 1: Single-Position Weight Threshold
            if rule.rule_type == AlertRuleType.WEIGHT_THRESHOLD.value:
                for h in holdings:
                    if (not rule.symbol or rule.symbol.upper() == h.ticker.upper()) and h.portfolio_weight_pct > rule.threshold:
                        alert = PortfolioAlertEventModel(
                            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                            user_id=user_id,
                            portfolio_id=user_context.portfolio.portfolio_id,
                            symbol=h.ticker,
                            alert_type="WEIGHT_THRESHOLD_CROSSED",
                            title=f"Position Weight Threshold: {h.ticker}",
                            message=f"{h.ticker} portfolio market weight ({h.portfolio_weight_pct}%) crossed the configured threshold of {rule.threshold}%.",
                            severity=AlertSeverity.WARNING.value,
                            trigger_metric="portfolio_weight_pct",
                            trigger_value=h.portfolio_weight_pct,
                            threshold_value=rule.threshold,
                            provenance=h.provenance.value,
                            is_read=False,
                            created_at=datetime.now(timezone.utc).isoformat()
                        )
                        alerts_emitted.append(alert)
                        if db:
                            await self._persist_alert(db, alert)

            # Rule 2: Volatility Threshold
            elif rule.rule_type == AlertRuleType.VOLATILITY_THRESHOLD.value:
                for h in holdings:
                    if (not rule.symbol or rule.symbol.upper() == h.ticker.upper()) and (h.volatility_pct or 0) > rule.threshold:
                        alert = PortfolioAlertEventModel(
                            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                            user_id=user_id,
                            portfolio_id=user_context.portfolio.portfolio_id,
                            symbol=h.ticker,
                            alert_type="VOLATILITY_ELEVATED",
                            title=f"Elevated Volatility: {h.ticker}",
                            message=f"{h.ticker} 30-day annualized volatility ({h.volatility_pct}%) exceeded the threshold of {rule.threshold}%.",
                            severity=AlertSeverity.WARNING.value,
                            trigger_metric="volatility_pct",
                            trigger_value=h.volatility_pct,
                            threshold_value=rule.threshold,
                            provenance=h.provenance.value,
                            is_read=False,
                            created_at=datetime.now(timezone.utc).isoformat()
                        )
                        alerts_emitted.append(alert)
                        if db:
                            await self._persist_alert(db, alert)

            # Rule 3: Sector Exposure Threshold
            elif rule.rule_type == AlertRuleType.SECTOR_EXPOSURE_THRESHOLD.value:
                for sec, sec_pct in user_context.portfolio.sector_allocations.items():
                    if sec_pct > rule.threshold:
                        alert = PortfolioAlertEventModel(
                            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                            user_id=user_id,
                            portfolio_id=user_context.portfolio.portfolio_id,
                            symbol=sec,
                            alert_type="SECTOR_CONCENTRATION",
                            title=f"Sector Concentration: {sec}",
                            message=f"{sec} sector allocation ({sec_pct}%) exceeded the concentration threshold of {rule.threshold}%.",
                            severity=AlertSeverity.INFO.value,
                            trigger_metric="sector_exposure_pct",
                            trigger_value=sec_pct,
                            threshold_value=rule.threshold,
                            provenance="CALCULATED",
                            is_read=False,
                            created_at=datetime.now(timezone.utc).isoformat()
                        )
                        alerts_emitted.append(alert)
                        if db:
                            await self._persist_alert(db, alert)

        # Also check watchlist anomalies
        if user_context.anomaly.total_anomalies > 0:
            for sym, anoms in user_context.anomaly.holding_anomalies_map.items():
                if anoms:
                    alert = PortfolioAlertEventModel(
                        alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        portfolio_id=user_context.portfolio.portfolio_id,
                        symbol=sym,
                        alert_type="ANOMALY_DETECTED",
                        title=f"Statistical Anomaly Observed: {sym}",
                        message=f"Statistical price return or volume surge anomaly identified for {sym}.",
                        severity=AlertSeverity.INFO.value,
                        trigger_metric="anomaly_count",
                        trigger_value=float(len(anoms)),
                        threshold_value=1.0,
                        provenance="MODEL_DERIVED",
                        is_read=False,
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    alerts_emitted.append(alert)

        return alerts_emitted

    async def _persist_alert(self, db: AsyncSession, alert: PortfolioAlertEventModel) -> None:
        """Helper to store generated alert into database."""
        try:
            repo = ResearchMemoryRepository(db)
            await repo.create_alert(
                user_id=alert.user_id,
                portfolio_id=alert.portfolio_id,
                symbol=alert.symbol,
                alert_type=alert.alert_type,
                title=alert.title,
                message=alert.message,
                severity=alert.severity,
                trigger_metric=alert.trigger_metric,
                trigger_value=alert.trigger_value,
                threshold_value=alert.threshold_value,
                provenance=alert.provenance
            )
        except Exception as ex:
            logger.debug(f"Failed to persist alert event: {ex}")

    async def create_rule(
        self,
        user_id: str,
        rule_type: str,
        threshold: float,
        symbol: Optional[str] = None,
        portfolio_id: Optional[str] = None,
        timeframe: str = "1d",
        db: Optional[AsyncSession] = None
    ) -> PortfolioAlertRuleModel:
        """Creates and stores a new alert rule for the user."""
        if db:
            repo = ResearchMemoryRepository(db)
            db_rule = await repo.create_alert_rule(
                user_id=user_id,
                rule_type=rule_type,
                threshold=threshold,
                symbol=symbol,
                portfolio_id=portfolio_id,
                timeframe=timeframe
            )
            return PortfolioAlertRuleModel(
                rule_id=db_rule.id,
                user_id=db_rule.user_id,
                portfolio_id=db_rule.portfolio_id,
                symbol=db_rule.symbol,
                rule_type=db_rule.rule_type,
                threshold=db_rule.threshold,
                timeframe=db_rule.timeframe,
                is_active=db_rule.is_active,
                created_at=db_rule.created_at.isoformat()
            )
        return PortfolioAlertRuleModel(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            rule_type=rule_type,
            threshold=threshold,
            timeframe=timeframe,
            is_active=True,
            created_at=datetime.now(timezone.utc).isoformat()
        )

    async def get_user_alerts(
        self,
        user_id: str,
        unread_only: bool = False,
        db: Optional[AsyncSession] = None
    ) -> List[PortfolioAlertEventModel]:
        """Fetches stored alerts for the user."""
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_alerts = await repo.get_user_alerts(user_id=user_id, unread_only=unread_only)
                return [
                    PortfolioAlertEventModel(
                        alert_id=a.id,
                        user_id=a.user_id,
                        portfolio_id=a.portfolio_id,
                        symbol=a.symbol,
                        alert_type=a.alert_type,
                        title=a.title,
                        message=a.message,
                        severity=a.severity,
                        trigger_metric=a.trigger_metric,
                        trigger_value=a.trigger_value,
                        threshold_value=a.threshold_value,
                        provenance=a.provenance,
                        is_read=a.is_read,
                        created_at=a.created_at.isoformat()
                    )
                    for a in db_alerts
                ]
            except Exception as ex:
                logger.warning(f"Error fetching alerts: {ex}")
        return []

    async def get_user_rules(
        self,
        user_id: str,
        db: Optional[AsyncSession] = None
    ) -> List[PortfolioAlertRuleModel]:
        """Fetches alert rules configured by the user."""
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_rules = await repo.get_user_alert_rules(user_id=user_id)
                return [
                    PortfolioAlertRuleModel(
                        rule_id=r.id,
                        user_id=r.user_id,
                        portfolio_id=r.portfolio_id,
                        symbol=r.symbol,
                        rule_type=r.rule_type,
                        threshold=r.threshold,
                        timeframe=r.timeframe,
                        is_active=r.is_active,
                        created_at=r.created_at.isoformat()
                    )
                    for r in db_rules
                ]
            except Exception as ex:
                logger.warning(f"Error fetching rules: {ex}")
        return []

    async def delete_rule(self, user_id: str, rule_id: str, db: Optional[AsyncSession] = None) -> bool:
        """Deletes an alert rule with ownership validation."""
        if db:
            repo = ResearchMemoryRepository(db)
            return await repo.delete_alert_rule(user_id=user_id, rule_id=rule_id)
        return True


alert_engine = PortfolioAlertEngine()
