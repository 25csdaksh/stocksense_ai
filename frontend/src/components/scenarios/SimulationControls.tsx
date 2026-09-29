"use client";

import React from "react";
import { Activity, AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/common/Button";

interface SimulationControlsProps {
  isLoading: boolean;
  loadingStage: string;
  error: string | null;
  onRetry: () => void;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  isLoading,
  loadingStage,
  error,
  onRetry,
}) => {
  if (!isLoading && !error) {
    return null;
  }

  return (
    <div className="space-y-3">
      {isLoading && (
        <div className="bg-primary/5 border border-primary/20 p-4 rounded-xl flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin shrink-0" />
          <div className="space-y-0.5 flex-1">
            <p className="text-xs font-semibold text-content">{loadingStage}</p>
            <div className="w-full bg-border/60 h-1.5 rounded-full overflow-hidden">
              <div className="bg-primary h-full rounded-full animate-pulse w-3/4" />
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-financial-loss/10 border border-financial-loss/30 p-4 rounded-xl flex items-start justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-financial-loss shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-financial-loss">Simulation Failed</p>
              <p className="text-[11px] text-content-muted mt-0.5">{error}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
          >
            Retry
          </Button>
        </div>
      )}
    </div>
  );
};
