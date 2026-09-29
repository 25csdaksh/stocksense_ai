"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { formatPercent, formatNumber } from "@/lib/utils";
import { EnrichedAnomalyItem } from "@/hooks/useAnomalyFeed";
import {
  ShieldAlert,
  ExternalLink,
  Sparkles,
  Zap,
  Activity,
  Gauge,
  Layers,
  CheckCircle2,
} from "lucide-react";

export interface AnomalyInspectorProps {
  anomaly: EnrichedAnomalyItem | null;
  isOpen: boolean;
  onClose: () => void;
  onTriggerAI: (ticker: string) => void;
}

export const AnomalyInspector: React.FC<AnomalyInspectorProps> = ({
  anomaly,
  isOpen,
  onClose,
  onTriggerAI,
}) => {
  const router = useRouter();

  if (!anomaly) return null;

  const isCritical = anomaly.severity === "CRITICAL";
  const isHigh = anomaly.severity === "HIGH";

  const handleOpenStock = () => {
    onClose();
    router.push(`/stocks/${encodeURIComponent(anomaly.ticker)}`);
  };

  const handleOpenResearch = () => {
    onClose();
    router.push(`/research?ticker=${encodeURIComponent(anomaly.ticker)}`);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Anomaly Diagnostic: ${anomaly.ticker}`}
      description={anomaly.company_name || anomaly.ticker}
      maxWidth="lg"
    >
      <div className="space-y-6 pt-2">
        {/* Banner Header */}
        <div className="flex items-center justify-between p-3.5 bg-surface-subtle rounded-xl border border-border">
          <div className="flex items-center gap-2.5">
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold ${
                isCritical ? "bg-financial-loss-bg text-financial-loss" : "bg-primary-light text-primary"
              }`}
            >
              {anomaly.ticker.slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-content text-sm">{anomaly.ticker}</span>
                <Badge
                  variant={isCritical ? "loss" : isHigh ? "gold" : "neutral"}
                  size="sm"
                  className="font-bold text-[9px] uppercase"
                >
                  {anomaly.severity} SEVERITY
                </Badge>
              </div>
              <p className="text-[11px] text-content-muted">{anomaly.anomaly_type} Detection</p>
            </div>
          </div>

          <div className="text-right text-xs">
            <span className="text-content-muted block text-[10px]">Detected:</span>
            <span className="font-bold text-content font-mono">{anomaly.formatted_time}</span>
          </div>
        </div>

        {/* Core telemetry highlights */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-surface-subtle/60 rounded-xl border border-border">
          <div>
            <span className="text-[10px] uppercase font-bold text-content-muted block">Observed Value</span>
            <span className="text-base font-bold text-content font-tabular">{anomaly.observed_value}</span>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-content-muted block">Expected Baseline</span>
            <span className="text-base font-bold text-content-muted font-tabular">{anomaly.expected_value}</span>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-content-muted block">Statistical Deviation</span>
            <span className="text-base font-bold text-financial-loss font-tabular">
              +{anomaly.z_score?.toFixed(2)}σ
            </span>
          </div>

          <div>
            <span className="text-[10px] uppercase font-bold text-content-muted block">Isolation Score</span>
            <span className="text-base font-bold text-primary font-tabular">
              {(anomaly.isolation_score ?? -0.35).toFixed(3)}
            </span>
          </div>
        </div>

        {/* Anomaly Summary text */}
        <div className="p-3.5 bg-surface border border-border rounded-xl space-y-1.5">
          <span className="text-[11px] font-bold text-content-muted uppercase tracking-wider block">
            Surveillance Summary &amp; Diagnostic Note
          </span>
          <p className="text-xs text-content leading-relaxed">{anomaly.summary}</p>
        </div>

        {/* Model info strip */}
        <div className="flex items-center justify-between p-3 bg-surface-subtle/50 rounded-xl border border-border text-xs text-content-muted">
          <span>Primary Classifier:</span>
          <span className="font-bold text-content">{anomaly.model_name}</span>
        </div>

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            onClick={handleOpenResearch}
            leftIcon={<Sparkles className="w-3.5 h-3.5 text-accent" />}
          >
            Investigate with Multi-Agent AI
          </Button>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleOpenStock}
              rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
            >
              View Stock Intelligence
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
