import React from "react";
import { cn, formatPercent, getChangeColor, getChangeBgColor } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Badge } from "./Badge";

export interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  isDemo?: boolean;
  className?: string;
  helperText?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  change,
  changeLabel = "vs prev close",
  icon,
  isDemo = false,
  className,
  helperText,
}) => {
  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;

  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-xl p-5 shadow-card transition-all duration-200 hover:shadow-card-hover",
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-content-muted">
          {label}
        </span>
        <div className="flex items-center gap-1.5">
          {isDemo && (
            <Badge variant="gold" size="sm">
              DEMO DATA
            </Badge>
          )}
          {icon && (
            <div className="p-2 rounded-lg bg-surface-subtle text-primary shrink-0">
              {icon}
            </div>
          )}
        </div>
      </div>

      <div className="mt-3">
        <h4 className="text-2xl font-bold tracking-tight text-content font-tabular">
          {value}
        </h4>

        {change !== undefined && (
          <div className="mt-2 flex items-center gap-2">
            <span
              className={cn(
                "inline-flex items-center gap-1 text-xs font-semibold px-1.5 py-0.5 rounded-md",
                getChangeBgColor(change)
              )}
            >
              {isPositive && <TrendingUp className="w-3.5 h-3.5" />}
              {isNegative && <TrendingDown className="w-3.5 h-3.5" />}
              {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5" />}
              <span>{formatPercent(change, { includeSign: true })}</span>
            </span>
            <span className="text-xs text-content-muted/80">{changeLabel}</span>
          </div>
        )}

        {helperText && (
          <p className="mt-2 text-xs text-content-muted">{helperText}</p>
        )}
      </div>
    </div>
  );
};
