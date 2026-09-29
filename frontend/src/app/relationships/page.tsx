"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Network,
  Activity,
  Layers,
  Sparkles,
  Sliders,
  TrendingUp,
  Share2,
} from "lucide-react";
import { api } from "@/lib/api";
import { RelationshipGraphData } from "@/types";

export default function RelationshipsPage() {
  const [matrixData, setMatrixData] = useState<any>(null);
  const [graphData, setGraphData] = useState<RelationshipGraphData | null>(null);
  const [threshold, setThreshold] = useState(0.45);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRelationships() {
      try {
        const [mRes, gRes] = await Promise.all([
          api.getCorrelationMatrix("pearson").catch(() => null),
          api.getRelationshipGraph(threshold).catch(() => null),
        ]);
        if (mRes) setMatrixData(mRes);
        if (gRes) setGraphData(gRes);
      } finally {
        setLoading(false);
      }
    }
    loadRelationships();
  }, [threshold]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Network className="w-5 h-5 text-primary" />
            <h1 className="text-2xl font-black text-slate-900 tracking-tight font-mono">
              Market Contagion & Relationship Graph
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Systemic correlation network, eigenvector centrality rankings, and Granger lead-lag econometric dynamics.
          </p>
        </div>

        {/* Threshold Slider */}
        <div className="flex items-center gap-3 bg-surface p-2 px-4 rounded-xl border border-border">
          <Sliders className="w-4 h-4 text-primary" />
          <span className="text-xs font-bold text-slate-600 font-mono">
            Edge Filter: |r| ≥ {threshold.toFixed(2)}
          </span>
          <input
            type="range"
            min="0.20"
            max="0.80"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-28 accent-primary"
          />
        </div>
      </div>

      {/* Network Metrics Cards */}
      {graphData?.network_metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-border">
            <span className="text-[11px] font-semibold text-slate-500">Total Asset Nodes</span>
            <div className="text-2xl font-black font-mono text-slate-900 mt-1">
              {graphData.network_metrics.total_nodes}
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-border">
            <span className="text-[11px] font-semibold text-slate-500">Correlation Edges</span>
            <div className="text-2xl font-black font-mono text-primary mt-1">
              {graphData.network_metrics.total_edges}
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-border">
            <span className="text-[11px] font-semibold text-slate-500">Graph Density</span>
            <div className="text-2xl font-black font-mono text-slate-900 mt-1">
              {(graphData.network_metrics.graph_density * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-border">
            <span className="text-[11px] font-semibold text-slate-500">Most Systemic Hub</span>
            <div className="text-2xl font-black font-mono text-gold-dark mt-1">
              {graphData.network_metrics.most_systemic_node}
            </div>
          </div>
        </div>
      )}

      {/* Grid: Correlation Matrix & Centrality Hubs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dynamic Correlation Matrix */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-border shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-slate-900">
                Rolling 90-Day Pearson Correlation Matrix
              </h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">PAIRWISE RETURN DYNAMICS</span>
          </div>

          <div className="p-5 overflow-x-auto flex-1">
            {matrixData?.assets && (
              <table className="w-full text-center border-collapse text-xs font-mono">
                <thead>
                  <tr>
                    <th className="p-2 border border-slate-200 bg-slate-50 text-slate-600 font-bold">
                      TICKER
                    </th>
                    {matrixData.assets.map((a: string) => (
                      <th key={a} className="p-2 border border-slate-200 bg-slate-50 font-bold text-slate-800">
                        {a}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrixData.matrix.map((row: number[], i: number) => {
                    const rowAsset = matrixData.assets[i];
                    return (
                      <tr key={rowAsset}>
                        <td className="p-2 border border-slate-200 bg-slate-50 font-bold text-slate-800">
                          {rowAsset}
                        </td>
                        {row.map((val: number, j: number) => {
                          const isSelf = i === j;
                          // Green for strong positive, Red for negative, Neutral for low
                          let bg = "bg-white";
                          let text = "text-slate-800";
                          if (!isSelf) {
                            if (val > 0.6) {
                              bg = "bg-emerald-50 text-emerald-900 font-bold";
                            } else if (val > 0.3) {
                              bg = "bg-emerald-50/40 text-emerald-800";
                            } else if (val < -0.1) {
                              bg = "bg-red-50 text-red-800";
                            }
                          } else {
                            bg = "bg-slate-100 font-bold text-slate-400";
                          }

                          return (
                            <td key={j} className={`p-2 border border-slate-200 ${bg}`}>
                              {val.toFixed(2)}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Systemic Centrality & Contagion Hubs */}
        <div className="bg-white rounded-2xl border border-border shadow-sm flex flex-col justify-between">
          <div className="p-5 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Share2 className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-slate-900">Systemic Eigenvector Centrality</h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">NETWORK RANKING</span>
          </div>

          <div className="p-5 space-y-3 flex-1 overflow-y-auto max-h-[460px]">
            {graphData?.nodes ? (
              graphData.nodes
                .sort((a, b) => b.eigenvector_centrality - a.eigenvector_centrality)
                .map((node) => (
                  <div
                    key={node.id}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 space-y-1.5 transition"
                  >
                    <div className="flex items-center justify-between">
                      <Link
                        href={`/workspace/${node.id}`}
                        className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-primary text-white"
                      >
                        {node.id}
                      </Link>
                      <span className="font-mono text-xs font-bold text-primary">
                        Score: {(node.eigenvector_centrality * 100).toFixed(1)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-600">
                      <span>{node.name}</span>
                      <span className="text-[11px] font-mono text-slate-400">
                        {node.degree} Links
                      </span>
                    </div>

                    <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden mt-1">
                      <div
                        className="bg-primary h-full rounded-full"
                        style={{ width: `${node.eigenvector_centrality * 100}%` }}
                      />
                    </div>
                  </div>
                ))
            ) : (
              <div className="text-center py-12 text-slate-400 text-xs">Loading network metrics...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
