"use client";

import React from "react";
import { AlertOctagon, Info } from "lucide-react";

export const ScenarioLimitations: React.FC = () => {
  return (
    <div className="bg-surface p-5 rounded-2xl border border-border shadow-card space-y-3">
      <div className="flex items-center justify-between border-b border-border pb-2.5">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-financial-loss" />
          <h4 className="text-xs font-bold text-content uppercase tracking-wider">
            Model Limitations & Regulatory Disclaimers
          </h4>
        </div>
        <span className="text-[10px] text-content-muted">Simulation Boundaries</span>
      </div>

      <div className="space-y-2 text-[11px] text-content-muted leading-relaxed">
        <p>
          • <strong>Simulations Are Not Forecasts:</strong> Stochastic Monte Carlo paths and historical stress tests are mathematical models of potential variance, not guaranteed predictions of future asset prices.
        </p>
        <p>
          • <strong>Regime Shifts & Liquidity:</strong> Extreme market events often alter correlation structures and liquidity conditions beyond historical calibrations.
        </p>
        <p>
          • <strong>Parameter Sensitivity:</strong> Results depend heavily on input assumptions for volatility, drift, and factor elasticity.
        </p>
        <p>
          • <strong>For Institutional Educational & Research Purposes Only:</strong> Not personalized investment advice or an offer to buy/sell securities.
        </p>
      </div>
    </div>
  );
};
