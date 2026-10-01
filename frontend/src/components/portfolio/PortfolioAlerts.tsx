"use client";

import React, { useState } from "react";
import { PortfolioAlertEvent, PortfolioAlertRule } from "@/types/portfolio-copilot";
import { Bell, AlertTriangle, Info, Check, Plus, Trash2 } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface PortfolioAlertsProps {
  alerts: PortfolioAlertEvent[];
  rules: PortfolioAlertRule[];
  onMarkRead?: (alertId: string) => void;
  onCreateRule?: (ruleType: string, threshold: number, symbol?: string) => void;
  onDeleteRule?: (ruleId: string) => void;
}

export const PortfolioAlerts: React.FC<PortfolioAlertsProps> = ({
  alerts,
  rules,
  onMarkRead,
  onCreateRule,
  onDeleteRule,
}) => {
  const [showRuleModal, setShowRuleModal] = useState(false);
  const [newRuleType, setNewRuleType] = useState("WEIGHT_THRESHOLD");
  const [newThreshold, setNewThreshold] = useState("25.0");
  const [newSymbol, setNewSymbol] = useState("");

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (onCreateRule) {
      onCreateRule(newRuleType, parseFloat(newThreshold) || 10.0, newSymbol || undefined);
      setShowRuleModal(false);
      setNewSymbol("");
    }
  };

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 shadow-card space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Bell className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-black text-content uppercase tracking-wider">
              Portfolio Alerts & Threshold Rules
            </h3>
            <p className="text-xs text-content-muted">
              Factual notifications triggered by weight shifts and volatility thresholds
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowRuleModal(true)}
          className="px-3 py-1.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm"
        >
          <Plus className="w-3.5 h-3.5" /> New Rule
        </button>
      </div>

      {/* Active Alerts List */}
      <div className="space-y-2.5">
        <h4 className="text-xs font-bold text-content uppercase tracking-wider">
          Active Alert Notifications ({alerts.length})
        </h4>

        {alerts.length > 0 ? (
          alerts.map((alt) => (
            <div
              key={alt.alert_id}
              className={`p-3.5 rounded-xl border transition-all flex items-start justify-between gap-3 text-xs ${
                alt.severity === "WARNING"
                  ? "bg-financial-warning/5 border-financial-warning/30"
                  : alt.severity === "CRITICAL"
                  ? "bg-financial-loss/5 border-financial-loss/30"
                  : "bg-surface-subtle border-border/70"
              }`}
            >
              <div className="flex items-start gap-2.5">
                {alt.severity === "WARNING" || alt.severity === "CRITICAL" ? (
                  <AlertTriangle className="w-4 h-4 text-financial-warning flex-shrink-0 mt-0.5" />
                ) : (
                  <Info className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                )}
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-content">{alt.title}</span>
                    <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-surface border border-border text-content-muted">
                      {alt.created_at ? alt.created_at.slice(0, 10) : ""}
                    </span>
                  </div>
                  <p className="text-content-muted leading-relaxed font-sans">{alt.message}</p>
                </div>
              </div>

              {!alt.is_read && onMarkRead && (
                <button
                  onClick={() => onMarkRead(alt.alert_id)}
                  className="px-2 py-1 rounded bg-surface hover:bg-surface-subtle border border-border text-[10px] font-bold text-content-muted hover:text-content transition-all flex items-center gap-1"
                >
                  <Check className="w-3 h-3 text-financial-gain" /> Dismiss
                </button>
              )}
            </div>
          ))
        ) : (
          <p className="text-xs text-content-muted italic bg-surface-subtle p-3.5 rounded-xl border border-border/60">
            No active threshold alerts triggered for current portfolio holdings.
          </p>
        )}
      </div>

      {/* Configured Rules */}
      {rules.length > 0 && (
        <div className="space-y-2.5 pt-2 border-t border-border">
          <h4 className="text-xs font-bold text-content uppercase tracking-wider">
            Active Threshold Rules ({rules.length})
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
            {rules.map((r) => (
              <div
                key={r.rule_id}
                className="p-3 bg-surface-subtle rounded-xl border border-border/70 flex items-center justify-between gap-2"
              >
                <div>
                  <span className="font-bold text-content block text-[11px]">{r.rule_type}</span>
                  <span className="text-[10px] text-content-muted">
                    Threshold: {r.threshold} {r.symbol ? `(${r.symbol})` : "(All Holdings)"}
                  </span>
                </div>
                {onDeleteRule && (
                  <button
                    onClick={() => onDeleteRule(r.rule_id)}
                    className="p-1.5 rounded-lg hover:bg-financial-loss/10 text-content-muted hover:text-financial-loss transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Rule Modal */}
      {showRuleModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-content">Configure Threshold Alert Rule</h3>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-content-muted mb-1 font-bold">Rule Trigger Type</label>
                <select
                  value={newRuleType}
                  onChange={(e) => setNewRuleType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-content text-xs font-mono"
                >
                  <option value="WEIGHT_THRESHOLD">Position Weight Threshold (%)</option>
                  <option value="VOLATILITY_THRESHOLD">Volatility Spike Threshold (%)</option>
                  <option value="SECTOR_EXPOSURE_THRESHOLD">Sector Exposure Threshold (%)</option>
                  <option value="PRICE_MOVE_PCT">Daily Price Move Threshold (%)</option>
                </select>
              </div>

              <div>
                <label className="block text-content-muted mb-1 font-bold">Threshold Value</label>
                <input
                  type="number"
                  step="any"
                  value={newThreshold}
                  onChange={(e) => setNewThreshold(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-content text-xs font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-content-muted mb-1 font-bold">Target Symbol (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. RELIANCE.NS (Leave empty for all holdings)"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-content text-xs font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowRuleModal(false)}
                  className="px-4 py-2 rounded-xl bg-surface-subtle hover:bg-surface border border-border text-xs font-bold text-content-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold"
                >
                  Create Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
