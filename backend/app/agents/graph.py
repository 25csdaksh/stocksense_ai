"""
LangGraph Multi-Agent StateGraph Orchestrator & SSE Stream Runner.
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from app.agents.state import AgentState
from app.agents.nodes import (
    supervisor_node,
    data_fetcher_node,
    quant_node,
    rag_node,
    synthesis_node
)


class MultiAgentGraphRunner:
    """Orchestrates multi-agent execution pipeline across Supervisor, Data, Quant, RAG, and Synthesis nodes."""

    async def execute(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        state: AgentState = {
            "query": query,
            "session_id": session_id,
            "ticker_focus": None,
            "intent": "MARKET_INTELLIGENCE",
            "thought_steps": [],
            "tool_calls": [],
            "data_context": {},
            "retrieved_citations": [],
            "ui_widgets": [],
            "final_answer": None,
            "guardrail_passed": False
        }

        # Step 1: Supervisor
        sup_out = supervisor_node(state)
        state.update(sup_out)

        # Step 2: Data Fetcher
        data_out = await data_fetcher_node(state)
        state["data_context"].update(data_out.get("data_context", {}))
        state["thought_steps"].extend(data_out.get("thought_steps", []))
        state["tool_calls"].extend(data_out.get("tool_calls", []))

        # Step 3: Quant Node
        quant_out = await quant_node(state)
        if quant_out:
            state["data_context"].update(quant_out.get("data_context", {}))
            state["thought_steps"].extend(quant_out.get("thought_steps", []))
            state["tool_calls"].extend(quant_out.get("tool_calls", []))
            state["ui_widgets"].extend(quant_out.get("ui_widgets", []))

        # Step 4: RAG Node
        rag_out = await rag_node(state)
        if rag_out:
            state["retrieved_citations"].extend(rag_out.get("retrieved_citations", []))
            state["thought_steps"].extend(rag_out.get("thought_steps", []))
            state["tool_calls"].extend(rag_out.get("tool_calls", []))

        # Step 5: Synthesis
        synth_out = synthesis_node(state)
        state.update(synth_out)

        return {
            "session_id": session_id,
            "query": query,
            "intent": state["intent"],
            "ticker_focus": state["ticker_focus"],
            "thought_steps": state["thought_steps"],
            "tool_calls": state["tool_calls"],
            "answer": state["final_answer"],
            "citations": state["retrieved_citations"],
            "ui_widgets": state["ui_widgets"],
            "guardrail_passed": state["guardrail_passed"]
        }

    async def stream(self, query: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        """Streams real-time thoughts, tool calls, UI widgets, and tokens over SSE."""
        state: AgentState = {
            "query": query,
            "session_id": session_id,
            "ticker_focus": None,
            "intent": "MARKET_INTELLIGENCE",
            "thought_steps": [],
            "tool_calls": [],
            "data_context": {},
            "retrieved_citations": [],
            "ui_widgets": [],
            "final_answer": None,
            "guardrail_passed": False
        }

        # 1. Supervisor
        sup_out = supervisor_node(state)
        state.update(sup_out)
        for th in sup_out.get("thought_steps", []):
            yield f"event: thought\ndata: {json.dumps(th)}\n\n"
        await asyncio.sleep(0.2)

        # 2. Data Fetcher
        data_out = await data_fetcher_node(state)
        state["data_context"].update(data_out.get("data_context", {}))
        for tc in data_out.get("tool_calls", []):
            yield f"event: tool_call\ndata: {json.dumps(tc)}\n\n"
        await asyncio.sleep(0.2)

        # 3. Quant or RAG
        quant_out = await quant_node(state)
        if quant_out:
            state["data_context"].update(quant_out.get("data_context", {}))
            for tc in quant_out.get("tool_calls", []):
                yield f"event: tool_call\ndata: {json.dumps(tc)}\n\n"
            for w in quant_out.get("ui_widgets", []):
                yield f"event: widget\ndata: {json.dumps(w)}\n\n"
            await asyncio.sleep(0.2)

        rag_out = await rag_node(state)
        if rag_out:
            state["retrieved_citations"].extend(rag_out.get("retrieved_citations", []))
            for tc in rag_out.get("tool_calls", []):
                yield f"event: tool_call\ndata: {json.dumps(tc)}\n\n"
            await asyncio.sleep(0.2)

        # 4. Synthesis
        synth_out = synthesis_node(state)
        state.update(synth_out)
        final_text = state["final_answer"] or ""

        # Stream tokens
        tokens = final_text.split(" ")
        for token in tokens:
            yield f"event: token\ndata: {json.dumps({'token': token + ' '})}\n\n"
            await asyncio.sleep(0.01)

        # Final Event
        yield f"event: final\ndata: {json.dumps({'full_answer': final_text, 'citations': state['retrieved_citations'], 'widgets': state['ui_widgets']})}\n\n"


agent_graph_runner = MultiAgentGraphRunner()
