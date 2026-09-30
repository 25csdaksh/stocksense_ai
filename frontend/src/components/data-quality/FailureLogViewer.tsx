"use client";

import React from "react";
import { OperationalFailureRecord, AlertSeverity } from "@/types/data-quality";
import { AlertOctagon, ShieldAlert, Info, AlertTriangle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface FailureLogViewerProps {
  failures?: OperationalFailureRecord[];
  isLoading?: boolean;
}

export const FailureLogViewer: React.FC<FailureLogViewerProps> = ({
  failures = [],
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="p-5 rounded-2xl bg-surface border border-border animate-pulse h-40" />
    );
  }

  const getSeverityBadge = (sev: AlertSeverity) => {
    switch (sev) {
      case "CRITICAL":
        return {
          bg: "bg-rose-500/10 text-rose-700 border-rose-500/30",
          icon: AlertOctagon,
        };
      case "WARNING":
        return {
          bg: "bg-amber-500/10 text-amber-700 border-amber-500/30",
          icon: AlertTriangle,
        };
      case "INFO":
      default:
        return {
          bg: "bg-sky-500/10 text-sky-700 border-sky-500/30",
          icon: Info,
        };
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-surface border border-border space-y-4 shadow-2xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-content">
            Operational Failure & Anomaly Audit Log
          </h3>
        </div>
        <span className="text-[10px] font-mono text-content-muted">
          Sanitized Telemetry (Zero Credential Leakage)
        </span>
      </div>

      {failures.length === 0 ? (
        <div className="p-6 rounded-xl bg-surface-subtle border border-border/80 text-center space-y-1">
          <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-600 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <p className="text-xs font-bold text-content">Zero Operational Failures</p>
          <p className="text-[11px] text-content-muted">
            All ingestion pipelines, cache lookups, and provider adapters are operating normally.
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto">
          {failures.map((f) => {
            const badge = getSeverityBadge(f.severity);
            const Icon = badge.icon;

            return (
              <div
                key={f.id}
                className="p-3 rounded-xl bg-surface-subtle border border-border/70 flex flex-col md:flex-row items-start md:items-center justify-between gap-2 text-xs"
              >
                <div className="flex items-start gap-2.5">
                  <div className={cn("p-1 rounded-lg border shrink-0 mt-0.5", badge.bg)}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <div className="space-y-0.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-primary font-mono">{f.component}</span>
                      {f.symbol && (
                        <span className="px-1.5 py-0.2 rounded bg-surface border border-border text-[10px] font-mono text-content font-bold">
                          {f.symbol}
                        </span>
                      )}
                      <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-surface border border-border text-content-muted">
                        {f.error_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-content-muted font-sans break-words">
                      {f.message}
                    </p>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-[10px] font-mono text-content-muted">
                    {new Date(f.timestamp).toLocaleTimeString()} UTC
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
