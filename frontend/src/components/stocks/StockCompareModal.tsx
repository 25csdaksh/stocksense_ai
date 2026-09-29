"use client";

import React, { useState } from "react";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { ArrowRightLeft, Sparkles, X, Layers, Check } from "lucide-react";

export interface StockCompareModalProps {
  isOpen: boolean;
  onClose: () => void;
  baseTicker: string;
  onCompareWithAI: (comparePrompt: string) => void;
}

const PEER_TICKERS: Record<string, string[]> = {
  "RELIANCE.NS": ["ONGC.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS"],
  "TCS.NS": ["INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
  "INFY.NS": ["TCS.NS", "WIPRO.NS", "HCLTECH.NS", "LTIM.NS"],
  "HDFCBANK.NS": ["ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
};

export const StockCompareModal: React.FC<StockCompareModalProps> = ({
  isOpen,
  onClose,
  baseTicker,
  onCompareWithAI,
}) => {
  const [selectedPeer, setSelectedPeer] = useState<string>(
    (PEER_TICKERS[baseTicker] && PEER_TICKERS[baseTicker][0]) || "TCS.NS"
  );

  if (!isOpen) return null;

  const peers = PEER_TICKERS[baseTicker] || ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"].filter((t) => t !== baseTicker);

  const handleRunComparison = () => {
    const prompt = `Compare ${baseTicker} with ${selectedPeer} across valuation multiples (P/E, P/B), operating profitability (ROE, Margins), technical momentum, and risk factors.`;
    onCompareWithAI(prompt);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-lg shadow-modal overflow-hidden animate-scale-in">
        {/* Header */}
        <div className="bg-primary text-white p-5 flex items-center justify-between border-b border-primary-light/20">
          <div className="flex items-center gap-2.5">
            <ArrowRightLeft className="w-5 h-5 text-accent" />
            <div>
              <h3 className="text-base font-bold text-white">Compare Stock Intelligence</h3>
              <p className="text-xs text-surface/80">Benchmark {baseTicker} against industry peers</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-surface/70 hover:text-white hover:bg-primary-light/20 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          <div className="p-3.5 bg-surface-subtle rounded-xl border border-border space-y-1 text-xs text-content-muted">
            <span className="font-bold text-content flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-primary" />
              Institutional Comparison Engine
            </span>
            <p className="leading-relaxed">
              Full dedicated multi-asset comparison workspace is scheduled for future release. You can run instant AI cross-asset fundamental and technical comparative analysis right now.
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-content uppercase tracking-wider block">
              Select Comparison Peer Ticker:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {peers.map((peer) => (
                <button
                  key={peer}
                  onClick={() => setSelectedPeer(peer)}
                  className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-between transition-all ${
                    selectedPeer === peer
                      ? "bg-primary-light/10 border-primary text-primary"
                      : "bg-surface border-border text-content hover:bg-surface-subtle"
                  }`}
                >
                  <span>{peer}</span>
                  {selectedPeer === peer && <Check className="w-4 h-4 text-primary" />}
                </button>
              ))}
            </div>
          </div>

          <div className="p-3 bg-surface-subtle/70 rounded-xl border border-border text-xs flex justify-between items-center font-tabular">
            <span className="text-content-muted">Comparison Pair:</span>
            <span className="font-bold text-content">
              {baseTicker} <span className="text-accent">VS</span> {selectedPeer}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-surface-subtle border-t border-border flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="gold"
            size="sm"
            onClick={handleRunComparison}
            leftIcon={<Sparkles className="w-4 h-4" />}
          >
            Run AI Comparison Analysis
          </Button>
        </div>
      </div>
    </div>
  );
};
