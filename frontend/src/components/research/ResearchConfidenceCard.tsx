"use client";

import React from "react";
import { ConfidenceLevel } from "@/types";
import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle } from "lucide-react";

interface ResearchConfidenceCardProps {
  level: ConfidenceLevel;
  rationale: string;
  provenanceSummary?: Record<string, string>;
}

export const ResearchConfidenceCard: React.FC<ResearchConfidenceCardProps> = ({
  level,
  rationale,
  provenanceSummary,
}) => {
  const getBadgeConfig = () => {
    switch (level) {
      case "HIGH":
        return {
          icon: <ShieldCheck className="w-5 h-5 text-financial-gain" />,
          bgColor: "bg-financial-gain/10 border-financial-gain/30",
          textColor: "text-financial-gain",
          label: "HIGH CONFIDENCE",
          desc: "Multi-pillar consistency across verified live/calculated data",
        };
      case "MEDIUM":
        return {
          icon: <ShieldCheck className="w-5 h-5 text-financial-warning" />,
          bgColor: "bg-financial-warning/10 border-financial-warning/30",
          textColor: "text-financial-warning",
          label: "MEDIUM CONFIDENCE",
          desc: "Adequate evidence base with minor staleness or partial demo coverage",
        };
      case "LOW":
        return {
          icon: <AlertTriangle className="w-5 h-5 text-orange-400" />,
          bgColor: "bg-orange-500/10 border-orange-500/30",
          textColor: "text-orange-400",
          label: "LOW CONFIDENCE",
          desc: "Limited evidence coverage; directional guidance only",
        };
      default:
        return {
          icon: <ShieldAlert className="w-5 h-5 text-financial-loss" />,
          bgColor: "bg-financial-loss/10 border-financial-loss/30",
          textColor: "text-financial-loss",
          label: "INSUFFICIENT DATA",
          desc: "Insufficient verified signals to form reliable analytical deductions",
        };
    }
  };

  const badge = getBadgeConfig();

  return (
    <div className={`p-4 rounded-2xl border ${badge.bgColor} backdrop-blur-sm space-y-3 transition-all`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          {badge.icon}
          <div>
            <span className={`text-xs font-black tracking-wider uppercase ${badge.textColor}`}>
              {badge.label}
            </span>
            <p className="text-[11px] text-content-muted leading-tight">{badge.desc}</p>
          </div>
        </div>
      </div>

      <p className="text-xs text-content leading-relaxed font-sans border-t border-border-subtle pt-2.5">
        {rationale}
      </p>

      {provenanceSummary && Object.keys(provenanceSummary).length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-border-subtle/50 text-[10px] font-tabular">
          {Object.entries(provenanceSummary).map(([key, val]) => (
            <div key={key} className="bg-surface/60 p-1.5 rounded-lg border border-border/50">
              <span className="text-content-muted block truncate font-medium">{key}</span>
              <span className="font-bold text-content">{val}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
