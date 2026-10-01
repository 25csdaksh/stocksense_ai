"""
MarketMind AI — Structured Evidence Graph.
Phase 6.9: Graph-based evidence representation mapping companies, financial metrics,
technical signals, anomalies, news articles, and risk metrics with typed relationship edges.
"""
from typing import Dict, Any, List, Optional
from app.ai.models import (
    EvidenceNode,
    EvidenceEdge,
    EdgeType,
    ResearchEvidence,
)


class EvidenceGraph:
    """Directed graph of financial evidence nodes and typed relationships."""

    def __init__(self):
        self._nodes: Dict[str, EvidenceNode] = {}
        self._edges: List[EvidenceEdge] = []
        self._adjacency: Dict[str, List[str]] = {}

    def add_node(self, node: EvidenceNode) -> None:
        """Adds or updates a node in the evidence graph."""
        self._nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.ASSOCIATED_WITH,
        weight: float = 1.0,
        description: Optional[str] = None
    ) -> EvidenceEdge:
        """Adds a typed relationship edge between two evidence nodes."""
        edge = EvidenceEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            description=description
        )
        self._edges.append(edge)
        if source_id in self._adjacency and target_id not in self._adjacency[source_id]:
            self._adjacency[source_id].append(target_id)
        return edge

    def ingest_evidence(self, evidence: ResearchEvidence) -> EvidenceNode:
        """Ingests atomic research evidence into the graph, attaching appropriate nodes and edges."""
        node_id = f"ev_{evidence.evidence_id}"
        node = EvidenceNode(
            id=node_id,
            node_type=evidence.category,
            label=f"{evidence.symbol or 'GLOBAL'}: {evidence.metric}",
            properties={
                "metric": evidence.metric,
                "value": evidence.value,
                "source": evidence.source,
                "provenance": evidence.provenance.value,
                "confidence": evidence.confidence,
                "timestamp": evidence.timestamp,
            }
        )
        self.add_node(node)

        # Attach to Company node if symbol is specified
        if evidence.symbol:
            company_node_id = f"comp_{evidence.symbol}"
            if company_node_id not in self._nodes:
                self.add_node(
                    EvidenceNode(
                        id=company_node_id,
                        node_type="Company",
                        label=evidence.symbol,
                        properties={"symbol": evidence.symbol}
                    )
                )
            self.add_edge(
                source_id=company_node_id,
                target_id=node_id,
                edge_type=EdgeType.DERIVED_FROM if evidence.provenance.value == "CALCULATED" else EdgeType.ASSOCIATED_WITH,
                description=f"{evidence.category} evidence for {evidence.symbol}"
            )

        return node

    def get_nodes(self) -> List[EvidenceNode]:
        return list(self._nodes.values())

    def get_edges(self) -> List[EvidenceEdge]:
        return self._edges

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the evidence graph for UI visualization."""
        return {
            "nodes": [n.model_dump() for n in self._nodes.values()],
            "edges": [e.model_dump() for e in self._edges],
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
        }
