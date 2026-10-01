"""
MarketMind AI — Personal Research Memory Service.
Phase 6.10: User-scoped research persistence, memory retrieval, and Redis caching.
Guarantees strict multi-tenant user isolation and zero cross-user memory leakage.
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.portfolio.models import ResearchMemoryItem
from app.db.repositories.research_memory_repository import ResearchMemoryRepository
from app.cache.redis_client import redis_client
from app.core.logging import logger


class ResearchMemoryService:
    """Manages user-scoped research memory records and isolated cache tiers."""

    def __init__(self):
        self.cache_ttl = 3600  # 1 hour cache for user research memory
        self._in_memory_cache: Dict[str, Dict[str, Any]] = {}

    def _get_cache_key(self, user_id: str, research_id: str) -> str:
        """Generates strictly user-isolated Redis key."""
        return f"research_memory:{user_id}:{research_id}"


    async def record_research_session(
        self,
        user_id: str,
        research_id: str,
        query: str,
        symbols: List[str],
        intent: str,
        depth: str = "STANDARD",
        report_summary: Optional[str] = None,
        evidence_count: int = 0,
        confidence_level: str = "MEDIUM",
        confidence_rationale: Optional[str] = None,
        provenance_summary: Optional[Dict[str, Any]] = None,
        key_metrics: Optional[Dict[str, Any]] = None,
        cited_sources: Optional[List[Dict[str, Any]]] = None,
        data_status: str = "DEMO",
        db: Optional[AsyncSession] = None
    ) -> ResearchMemoryItem:
        """Stores research memory in database and user-isolated Redis cache."""
        item = ResearchMemoryItem(
            research_id=research_id,
            query=query,
            symbols=symbols,
            intent=intent,
            execution_depth=depth,
            created_at=datetime.now(timezone.utc).isoformat(),
            report_summary=report_summary,
            evidence_count=evidence_count,
            confidence_level=confidence_level,
            confidence_rationale=confidence_rationale,
            provenance_summary=provenance_summary or {},
            key_metrics=key_metrics or {},
            cited_sources=cited_sources or [],
            data_status=data_status,
            research_version="6.10"
        )

        # 1. DB Persistence
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                await repo.save_memory(
                    user_id=user_id,
                    research_id=research_id,
                    query=query,
                    symbols=symbols,
                    intent=intent,
                    execution_depth=depth,
                    report_summary=report_summary,
                    evidence_count=evidence_count,
                    confidence_level=confidence_level,
                    confidence_rationale=confidence_rationale,
                    provenance_summary=provenance_summary,
                    key_metrics=key_metrics,
                    cited_sources=cited_sources,
                    data_status=data_status,
                    research_version="6.10"
                )
            except Exception as ex:
                logger.warning(f"Error persisting research memory to DB: {ex}")

        # 2. Redis User-Isolated Cache
        cache_key = self._get_cache_key(user_id, research_id)
        self._in_memory_cache[cache_key] = item.model_dump()
        try:
            await redis_client.set(
                cache_key,
                json.dumps(item.model_dump(), default=str),
                expire_seconds=self.cache_ttl
            )
        except Exception as ex:
            logger.debug(f"Redis memory cache set failed: {ex}")

        return item

    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        db: Optional[AsyncSession] = None
    ) -> List[ResearchMemoryItem]:
        """Retrieves recent research memories for the specified user."""
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_items = await repo.get_user_memories(user_id=user_id, limit=limit, offset=offset)
                return [
                    ResearchMemoryItem(
                        research_id=m.research_id,
                        query=m.query,
                        symbols=m.symbols or [],
                        intent=m.intent,
                        execution_depth=m.execution_depth,
                        created_at=m.created_at.isoformat(),
                        report_summary=m.report_summary,
                        evidence_count=m.evidence_count,
                        confidence_level=m.confidence_level,
                        confidence_rationale=m.confidence_rationale,
                        provenance_summary=m.provenance_summary or {},
                        key_metrics=m.key_metrics or {},
                        cited_sources=m.cited_sources or [],
                        data_status=m.data_status,
                        research_version=m.research_version
                    )
                    for m in db_items
                ]
            except Exception as ex:
                logger.warning(f"Error reading memories from DB: {ex}")

        # In-memory fallback
        user_prefix = f"research_memory:{user_id}:"
        user_items = [
            ResearchMemoryItem(**v)
            for k, v in self._in_memory_cache.items()
            if k.startswith(user_prefix)
        ]
        return user_items[offset:offset + limit]

    async def get_memory_by_id(
        self,
        user_id: str,
        research_id: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[ResearchMemoryItem]:
        """Retrieves a specific memory item enforcing user ownership."""
        cache_key = self._get_cache_key(user_id, research_id)

        # 1. Check Redis Cache
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return ResearchMemoryItem(**json.loads(cached))
        except Exception:
            pass

        # 2. Check in-memory fallback
        if cache_key in self._in_memory_cache:
            return ResearchMemoryItem(**self._in_memory_cache[cache_key])

        # 3. Query DB

        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_mem = await repo.get_memory_by_id(user_id=user_id, research_id=research_id)
                if db_mem:
                    return ResearchMemoryItem(
                        research_id=db_mem.research_id,
                        query=db_mem.query,
                        symbols=db_mem.symbols or [],
                        intent=db_mem.intent,
                        execution_depth=db_mem.execution_depth,
                        created_at=db_mem.created_at.isoformat(),
                        report_summary=db_mem.report_summary,
                        evidence_count=db_mem.evidence_count,
                        confidence_level=db_mem.confidence_level,
                        confidence_rationale=db_mem.confidence_rationale,
                        provenance_summary=db_mem.provenance_summary or {},
                        key_metrics=db_mem.key_metrics or {},
                        cited_sources=db_mem.cited_sources or [],
                        data_status=db_mem.data_status,
                        research_version=db_mem.research_version
                    )
            except Exception as ex:
                logger.warning(f"Error querying memory by ID: {ex}")

        return None

    async def get_latest_symbol_memory(
        self,
        user_id: str,
        symbol: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[ResearchMemoryItem]:
        """Finds the most recent research session for a given symbol."""
        if db:
            try:
                repo = ResearchMemoryRepository(db)
                db_mem = await repo.get_latest_memory_for_symbol(user_id=user_id, symbol=symbol)
                if db_mem:
                    return ResearchMemoryItem(
                        research_id=db_mem.research_id,
                        query=db_mem.query,
                        symbols=db_mem.symbols or [],
                        intent=db_mem.intent,
                        execution_depth=db_mem.execution_depth,
                        created_at=db_mem.created_at.isoformat(),
                        report_summary=db_mem.report_summary,
                        evidence_count=db_mem.evidence_count,
                        confidence_level=db_mem.confidence_level,
                        confidence_rationale=db_mem.confidence_rationale,
                        provenance_summary=db_mem.provenance_summary or {},
                        key_metrics=db_mem.key_metrics or {},
                        cited_sources=db_mem.cited_sources or [],
                        data_status=db_mem.data_status,
                        research_version=db_mem.research_version
                    )
            except Exception as ex:
                logger.warning(f"Error searching symbol memory: {ex}")

        return None


memory_service = ResearchMemoryService()
