"use client";

import React from "react";
import { ProviderHealthReport } from "@/types/data-quality";
import { Activity, ShieldCheck, AlertCircle, KeyRound, Radio } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProviderHealthMatrixProps {
  providers?: ProviderHealthReport[];
  isLoading?: boolean;
}

export const ProviderHealthMatrix: React.FC<ProviderHealthMatrixProps> = ({
  providers = [],
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="p-5 rounded-2xl bg-surface border border-border animate-pulse h-48" />
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "LIVE":
        return {
          bg: "bg-emerald-500/10 text-emerald-700 border-emerald-500/30",
          icon: Radio,
          label: "LIVE ACTIVE",
        };
      case "DEMO":
        return {
          bg: "bg-primary-light/40 text-primary border-primary/20",
          icon: Activity,
          label: "DEMO SIMULATOR",
        };
      case "CONFIGURATION_REQUIRED":
        return {
          bg: "bg-amber-500/10 text-amber-700 border-amber-500/30",
          icon: KeyRound,
          label: "CONFIG REQUIRED",
        };
      case "RATE_LIMITED":
        return {
          bg: "bg-purple-500/10 text-purple-700 border-purple-500/30",
          icon: AlertCircle,
          label: "RATE LIMITED",
        };
      case "DEGRADED":
      case "DOWN":
      default:
        return {
          bg: "bg-rose-500/10 text-rose-700 border-rose-500/30",
          icon: AlertCircle,
          label: status,
        };
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-surface border border-border space-y-4 shadow-2xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-content">
            External Provider Health & Latency Telemetry
          </h3>
        </div>
        <span className="text-[10px] font-mono text-content-muted">
          P50 / P95 Percentiles & Rate Limits
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-border text-[10px] font-bold uppercase tracking-wider text-content-muted">
              <th className="pb-2.5">Provider</th>
              <th className="pb-2.5">Market</th>
              <th className="pb-2.5">Status</th>
              <th className="pb-2.5 text-right">Avg Latency</th>
              <th className="pb-2.5 text-right">P95 Latency</th>
              <th className="pb-2.5 text-right">Req / Fails</th>
              <th className="pb-2.5 text-right">Error Rate</th>
              <th className="pb-2.5 text-right">Rate Limits</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {providers.map((p) => {
              const badge = getStatusBadge(p.status);
              const BadgeIcon = badge.icon;

              return (
                <tr key={p.provider_name} className="hover:bg-surface-subtle/50 transition-colors">
                  <td className="py-3 font-semibold text-primary flex items-center gap-2">
                    <span className="font-mono text-xs">{p.provider_name}</span>
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border text-[10px] font-mono font-bold text-content">
                      {p.market}
                    </span>
                  </td>
                  <td className="py-3">
                    <span
                      className={cn(
                        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border",
                        badge.bg
                      )}
                    >
                      <BadgeIcon className="w-3 h-3" />
                      {badge.label}
                    </span>
                  </td>
                  <td className="py-3 text-right font-mono text-content">
                    {p.latency?.average_ms ?? 0} ms
                  </td>
                  <td className="py-3 text-right font-mono text-content">
                    {p.latency?.p95_ms ?? 0} ms
                  </td>
                  <td className="py-3 text-right font-mono text-content-muted">
                    <span className="text-content font-medium">{p.success_count}</span> /{" "}
                    <span className={p.failure_count > 0 ? "text-rose-600 font-bold" : "text-content-muted"}>
                      {p.failure_count}
                    </span>
                  </td>
                  <td className="py-3 text-right font-mono">
                    <span
                      className={cn(
                        "font-bold",
                        p.error_rate_pct > 5 ? "text-rose-600" : "text-emerald-600"
                      )}
                    >
                      {p.error_rate_pct}%
                    </span>
                  </td>
                  <td className="py-3 text-right font-mono text-content">
                    {p.rate_limit_hits}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
