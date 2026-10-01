"use client";

import React from "react";
import { Table } from "@/components/common/Table";
import { Badge } from "@/components/common/Badge";
import { Layers, CheckCircle, Database } from "lucide-react";

interface EvidenceMatrixProps {
  comparisonData?: Array<Record<string, any>>;
  rawEvidenceCount?: number;
}

export const EvidenceMatrix: React.FC<EvidenceMatrixProps> = ({
  comparisonData,
  rawEvidenceCount = 0,
}) => {
  if (!comparisonData || comparisonData.length === 0) return null;

  return (
    <div className="bg-surface border border-border rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-accent/10 text-accent flex items-center justify-center font-bold text-xs">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-content uppercase tracking-wider">
              Side-by-Side Comparative Evidence Matrix
            </h4>
            <p className="text-[10px] text-content-muted">
              Standardized multi-factor comparison across {comparisonData.length} target instruments
            </p>
          </div>
        </div>

        <Badge variant="outline" size="sm">
          {comparisonData.length} Instruments
        </Badge>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border/70">
        <table className="w-full text-xs text-left font-sans">
          <thead className="bg-surface-subtle text-content-muted font-bold text-[10px] uppercase tracking-wider border-b border-border/70">
            <tr>
              <th className="p-3">Symbol</th>
              <th className="p-3 text-right">Last Price</th>
              <th className="p-3 text-right">P/E Ratio</th>
              <th className="p-3 text-right">ROE %</th>
              <th className="p-3 text-right">14d RSI</th>
              <th className="p-3 text-right">Ann. Vol %</th>
              <th className="p-3">Regime Bias</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50 text-[11px] font-tabular">
            {comparisonData.map((row, idx) => (
              <tr key={row.symbol || idx} className="hover:bg-surface-subtle/50 transition-colors">
                <td className="p-3 font-extrabold text-content">{row.symbol}</td>
                <td className="p-3 text-right font-semibold">
                  {row.latest_price != null ? `₹${row.latest_price}` : "N/A"}
                </td>
                <td className="p-3 text-right text-content-muted">
                  {row.pe_ratio != null ? row.pe_ratio : "—"}
                </td>
                <td className="p-3 text-right font-medium">
                  {row.roe_pct != null ? `${row.roe_pct}%` : "—"}
                </td>
                <td className="p-3 text-right">
                  {row.rsi_14 != null ? (
                    <span
                      className={`font-semibold ${
                        row.rsi_14 > 70
                          ? "text-financial-warning"
                          : row.rsi_14 < 30
                          ? "text-financial-gain"
                          : "text-content"
                      }`}
                    >
                      {row.rsi_14}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="p-3 text-right text-content-muted">
                  {row.annualized_volatility_pct != null
                    ? `${row.annualized_volatility_pct}%`
                    : "—"}
                </td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded-full bg-surface-subtle border border-border text-[9px] font-bold text-content-muted">
                    {row.trend_regime || "NEUTRAL"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
