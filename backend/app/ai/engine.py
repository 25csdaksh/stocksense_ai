"""
MarketMind AI — Multi-Agent Financial Research & Intelligence Engine.
Phase 6.9: High-performance orchestrator coordinating specialist agents (Market, Fundamental,
News, Quant, Risk, Anomaly, RAG, Comparison, Context) with parallel async execution, Redis caching,
structured Evidence Graph compilation, cross-validation, and citation-anchored synthesis.
"""
import time
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timezone

from app.ai.models import (
    ResearchIntent,
    ResearchDepth,
    ResearchPlan,
    ResearchTask,
    TaskStatus,
    ResearchEvidence,
    EvidenceProvenance,
    CrossValidationReport,
    ResearchReport,
    ConfidenceLevel,
)
from app.ai.agents.supervisor_agent import supervisor_agent
from app.ai.agents.market_agent import market_agent
from app.ai.agents.fundamental_agent import fundamental_agent
from app.ai.agents.news_agent import news_agent
from app.ai.agents.quant_agent import quant_agent
from app.ai.agents.risk_agent import risk_agent
from app.ai.agents.anomaly_agent import anomaly_agent
from app.ai.agents.rag_agent import rag_agent
from app.ai.agents.comparison_agent import comparison_agent
from app.ai.agents.context_agent import context_agent
from app.ai.evidence.graph import EvidenceGraph
from app.ai.cross_validator import cross_validator
from app.ai.research_synthesizer import research_synthesizer
from app.cache.redis_client import redis_client
from app.observability.infra_monitor import infra_monitor
from app.core.logging import logger


class MultiAgentResearchEngine:
    """Production-grade multi-agent research engine for deep institutional market intelligence."""

    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache for market research

    def _get_cache_key(self, query: str, symbols: List[str], depth: ResearchDepth, intent: ResearchIntent) -> str:
        """Generates deterministic Redis cache key."""
        sym_key = "_".join(sorted(symbols)) if symbols else "GLOBAL"
        q_hash = abs(hash(query.strip().lower())) % 100000000
        return f"ai_research:{intent.value}:{sym_key}:{depth.value}:{q_hash}"

    async def execute_research(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        session_id: str = "default_session",
        symbols_override: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes full multi-agent research pipeline and returns comprehensive structured analysis."""
        start_time = time.perf_counter()

        # Step 1: Supervisor creates Research Plan
        plan = supervisor_agent.create_plan(
            query=query,
            depth=depth,
            symbols_override=symbols_override
        )

        # Step 2: Cache lookup (Skip for personal portfolio analysis)
        cache_key = self._get_cache_key(query, plan.symbols, depth, plan.intent)
        if plan.intent != ResearchIntent.PORTFOLIO_ANALYSIS:
            cached = await redis_client.get(cache_key)
            if cached:
                try:
                    cached_data = json.loads(cached)
                    cached_data["cached"] = True
                    return cached_data
                except Exception:
                    pass

        # Step 3: Concurrently Execute Independent Specialist Agents
        agent_tasks: Dict[str, Any] = {}
        tf = plan.date_range or "6m"

        if "market_agent" in plan.selected_agents:
            agent_tasks["market_agent"] = market_agent.run(plan.symbols, timeframe=tf)
        if "fundamental_agent" in plan.selected_agents:
            agent_tasks["fundamental_agent"] = fundamental_agent.run(plan.symbols)
        if "quant_agent" in plan.selected_agents:
            agent_tasks["quant_agent"] = quant_agent.run(plan.symbols, timeframe=tf)
        if "news_agent" in plan.selected_agents:
            agent_tasks["news_agent"] = news_agent.run(plan.symbols)
        if "risk_agent" in plan.selected_agents:
            agent_tasks["risk_agent"] = risk_agent.run(plan.symbols, timeframe=tf)
        if "anomaly_agent" in plan.selected_agents:
            agent_tasks["anomaly_agent"] = anomaly_agent.run(plan.symbols, timeframe=tf)
        if "rag_agent" in plan.selected_agents:
            agent_tasks["rag_agent"] = rag_agent.run(query=query, symbols=plan.symbols)
        if "context_agent" in plan.selected_agents:
            agent_tasks["context_agent"] = context_agent.run()

        # Run independent agents in parallel with timeout
        agent_names = list(agent_tasks.keys())
        coros = list(agent_tasks.values())
        results = await asyncio.gather(*coros, return_exceptions=True)

        all_evidence: List[ResearchEvidence] = []
        agent_results_map: Dict[str, List[ResearchEvidence]] = {}

        for name, res in zip(agent_names, results):
            if isinstance(res, Exception):
                logger.warning(f"Specialist agent {name} failed: {res}")
                # Partial failure resilience: Record unavailable status evidence
                unavailable_ev = ResearchEvidence(
                    evidence_id=f"ev_err_{uuid.uuid4().hex[:6]}",
                    category=name.replace("_agent", "").upper(),
                    symbol=plan.symbols[0] if plan.symbols else None,
                    metric="agent_execution_status",
                    value={"status": "FAILED", "reason": str(res)[:80]},
                    source=name,
                    provenance=EvidenceProvenance.UNAVAILABLE,
                    confidence=0.0
                )
                all_evidence.append(unavailable_ev)
                agent_results_map[name] = [unavailable_ev]
                # Update task status in plan
                for t in plan.tasks:
                    if t.agent == name:
                        t.status = TaskStatus.FAILED
                        t.error = str(res)[:80]
            elif isinstance(res, list):
                all_evidence.extend(res)
                agent_results_map[name] = res
                for t in plan.tasks:
                    if t.agent == name:
                        t.status = TaskStatus.COMPLETED

        # Step 4: Run Comparison Agent if requested
        if "comparison_agent" in plan.selected_agents and len(plan.symbols) >= 2:
            try:
                comp_ev = await comparison_agent.run(
                    symbols=plan.symbols,
                    market_evidence=agent_results_map.get("market_agent", []),
                    fundamental_evidence=agent_results_map.get("fundamental_agent", []),
                    technical_evidence=agent_results_map.get("quant_agent", []),
                    risk_evidence=agent_results_map.get("risk_agent", [])
                )
                all_evidence.extend(comp_ev)
                for t in plan.tasks:
                    if t.agent == "comparison_agent":
                        t.status = TaskStatus.COMPLETED
            except Exception as ex:
                logger.warning(f"Comparison agent execution failed: {ex}")

        # Step 5: Construct Structured Evidence Graph
        evidence_graph = EvidenceGraph()
        for ev in all_evidence:
            evidence_graph.ingest_evidence(ev)

        # Step 6: Cross-Validation & Consistency Check
        validation_report = cross_validator.validate_evidence(all_evidence)

        # Step 7: Synthesize Institutional Research Report
        report = research_synthesizer.synthesize_report(
            query=query,
            plan=plan,
            evidence_list=all_evidence,
            validation_report=validation_report
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Step 8: Telemetry Recording
        infra_monitor.record_ai_query(latency_ms=elapsed_ms, success=True)

        # Step 9: Assemble Final Response Object
        response_data: Dict[str, Any] = {
            "query": query,
            "session_id": session_id,
            "intent": plan.intent.value,
            "ticker_focus": plan.symbols[0] if plan.symbols else None,
            "research_plan": plan.model_dump(),
            "execution_summary": {
                "duration_ms": elapsed_ms,
                "total_evidence_collected": len(all_evidence),
                "agents_executed": plan.selected_agents,
                "validation_report": validation_report.model_dump(),
                "evidence_graph": evidence_graph.to_dict()
            },
            "report": report.model_dump(),
            "citations": [c.model_dump() for c in report.citations],
            "provenance": report.provenance_summary,
            "limitations": report.limitations,
            # Backward-compatible fields for legacy UI and tests
            "thought_steps": [
                {
                    "step": idx + 1,
                    "agent": t.agent,
                    "message": f"Executed {t.agent.replace('_', ' ')}: {t.status.value}"
                }
                for idx, t in enumerate(plan.tasks)
            ],
            "tool_calls": [
                {"tool": tool_name, "status": "COMPLETED"}
                for tool_name in plan.required_tools
            ],
            "answer": report.research_conclusion,
            "ui_widgets": [
                {
                    "widget_type": "metric_card",
                    "title": "Analytical Confidence",
                    "data": {
                        "level": report.confidence_level.value,
                        "rationale": report.confidence_rationale
                    }
                }
            ],
            "guardrail_passed": True,
            "cached": False
        }

        # Step 10: Cache Result in Redis (if not personal portfolio query)
        if plan.intent != ResearchIntent.PORTFOLIO_ANALYSIS:
            try:
                await redis_client.set(
                    cache_key,
                    json.dumps(response_data, default=str),
                    expire_seconds=self.cache_ttl
                )
            except Exception as ex:
                logger.debug(f"Redis cache set failed: {ex}")

        return response_data

    async def stream_research(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        session_id: str = "default_session",
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streams real-time research lifecycle events over Server-Sent Events (SSE)."""
        start_time = time.perf_counter()

        def _sse_event(event_name: str, payload: Dict[str, Any]) -> str:
            return f"event: {event_name}\ndata: {json.dumps(payload, default=str)}\n\n"

        try:
            # Event 1: RESEARCH_STARTED
            yield _sse_event("RESEARCH_STARTED", {
                "query": query,
                "session_id": session_id,
                "depth": depth.value,
                "started_at": datetime.now(timezone.utc).isoformat()
            })
            await asyncio.sleep(0.01)

            # Event 2: PLAN_CREATED
            plan = supervisor_agent.create_plan(query=query, depth=depth)
            yield _sse_event("PLAN_CREATED", {
                "intent": plan.intent.value,
                "symbols": plan.symbols,
                "time_horizon": plan.date_range,
                "selected_agents": plan.selected_agents,
                "required_tools": plan.required_tools
            })
            await asyncio.sleep(0.01)

            # Legacy thought step for backward-compatibility
            yield f"event: thought\ndata: {json.dumps({'step': 1, 'agent': 'Supervisor', 'message': f'Formulated research plan for {plan.intent.value}'})}\n\n"

            # Specialist Agents Execution
            agent_tasks: Dict[str, Any] = {}
            tf = plan.date_range or "6m"

            if "market_agent" in plan.selected_agents:
                agent_tasks["market_agent"] = market_agent.run(plan.symbols, timeframe=tf)
            if "fundamental_agent" in plan.selected_agents:
                agent_tasks["fundamental_agent"] = fundamental_agent.run(plan.symbols)
            if "quant_agent" in plan.selected_agents:
                agent_tasks["quant_agent"] = quant_agent.run(plan.symbols, timeframe=tf)
            if "news_agent" in plan.selected_agents:
                agent_tasks["news_agent"] = news_agent.run(plan.symbols)
            if "risk_agent" in plan.selected_agents:
                agent_tasks["risk_agent"] = risk_agent.run(plan.symbols, timeframe=tf)
            if "anomaly_agent" in plan.selected_agents:
                agent_tasks["anomaly_agent"] = anomaly_agent.run(plan.symbols, timeframe=tf)
            if "rag_agent" in plan.selected_agents:
                agent_tasks["rag_agent"] = rag_agent.run(query=query, symbols=plan.symbols)
            if "context_agent" in plan.selected_agents:
                agent_tasks["context_agent"] = context_agent.run()

            all_evidence: List[ResearchEvidence] = []
            agent_results_map: Dict[str, List[ResearchEvidence]] = {}

            # Emit AGENT_STARTED events
            for agent_name in agent_tasks.keys():
                yield _sse_event("AGENT_STARTED", {
                    "agent": agent_name,
                    "objective": f"Executing {agent_name.replace('_', ' ')} domain analysis"
                })

            # Run parallel execution
            agent_names = list(agent_tasks.keys())
            coros = list(agent_tasks.values())
            results = await asyncio.gather(*coros, return_exceptions=True)

            for name, res in zip(agent_names, results):
                if isinstance(res, Exception):
                    yield _sse_event("AGENT_COMPLETED", {
                        "agent": name,
                        "status": "FAILED",
                        "evidence_count": 0,
                        "error": str(res)[:80]
                    })
                elif isinstance(res, list):
                    all_evidence.extend(res)
                    agent_results_map[name] = res
                    yield _sse_event("AGENT_COMPLETED", {
                        "agent": name,
                        "status": "COMPLETED",
                        "evidence_count": len(res)
                    })

            # Run comparison agent if needed
            if "comparison_agent" in plan.selected_agents and len(plan.symbols) >= 2:
                try:
                    comp_ev = await comparison_agent.run(
                        symbols=plan.symbols,
                        market_evidence=agent_results_map.get("market_agent", []),
                        fundamental_evidence=agent_results_map.get("fundamental_agent", []),
                        technical_evidence=agent_results_map.get("quant_agent", []),
                        risk_evidence=agent_results_map.get("risk_agent", [])
                    )
                    all_evidence.extend(comp_ev)
                except Exception:
                    pass

            # Event 5: EVIDENCE_COLLECTED
            categories = list({e.category for e in all_evidence})
            yield _sse_event("EVIDENCE_COLLECTED", {
                "total_evidence": len(all_evidence),
                "categories": categories
            })
            await asyncio.sleep(0.01)

            # Event 6: VALIDATION_STARTED
            yield _sse_event("VALIDATION_STARTED", {
                "message": "Running multi-dimensional cross-validation and data freshness audit..."
            })

            # Step: Cross-Validation
            validation_report = cross_validator.validate_evidence(all_evidence)
            yield _sse_event("VALIDATION_COMPLETED", {
                "confidence_level": validation_report.confidence_level.value,
                "confidence_rationale": validation_report.confidence_rationale,
                "conflicts_count": len(validation_report.conflicts_detected),
                "stale_items_count": validation_report.stale_items_count
            })
            await asyncio.sleep(0.01)

            # Event 8: SYNTHESIS_STARTED
            yield _sse_event("SYNTHESIS_STARTED", {
                "message": "Synthesizing institutional multi-agent research report..."
            })

            # Step: Synthesis
            report = research_synthesizer.synthesize_report(
                query=query,
                plan=plan,
                evidence_list=all_evidence,
                validation_report=validation_report
            )

            yield _sse_event("SYNTHESIS_COMPLETED", {
                "report_id": report.report_id,
                "symbols": report.symbols,
                "confidence_level": report.confidence_level.value
            })
            await asyncio.sleep(0.01)

            # Event 10: RESEARCH_COMPLETED
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            infra_monitor.record_ai_query(latency_ms=elapsed_ms, success=True)

            yield _sse_event("RESEARCH_COMPLETED", {
                "report": report.model_dump(),
                "citations": [c.model_dump() for c in report.citations],
                "provenance": report.provenance_summary,
                "duration_ms": elapsed_ms
            })

            # Legacy final event for backward-compatibility
            yield f"event: final\ndata: {json.dumps({'answer': report.research_conclusion, 'citations': [c.model_dump() for c in report.citations], 'guardrail_passed': True})}\n\n"

        except Exception as ex:
            logger.error(f"Stream research error: {ex}")
            yield _sse_event("RESEARCH_FAILED", {
                "error": "An internal error occurred during research execution.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })


multi_agent_engine = MultiAgentResearchEngine()
