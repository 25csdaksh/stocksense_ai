"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { AlertTriangle, RotateCcw, LayoutDashboard } from "lucide-react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error internally if necessary without exposing to UI
  }, [error]);

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-md w-full bg-surface p-8 rounded-2xl border border-border shadow-card space-y-6">
        <div className="w-12 h-12 rounded-2xl bg-financial-loss/10 border border-financial-loss/20 flex items-center justify-center text-financial-loss mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>

        <div className="space-y-1.5">
          <Badge variant="loss" size="sm">
            INTERFACE EXCEPTION
          </Badge>
          <h2 className="text-xl font-bold tracking-tight text-content">
            MarketMind AI Encountered an Interface Error
          </h2>
          <p className="text-xs text-content-muted leading-relaxed">
            An unexpected error occurred while processing market telemetry or rendering workspace components.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Button
            variant="outline"
            size="md"
            onClick={() => reset()}
            leftIcon={<RotateCcw className="w-4 h-4" />}
            className="w-full sm:w-auto"
          >
            Retry Workspace
          </Button>
          <Link href="/dashboard" className="w-full sm:w-auto">
            <Button
              variant="primary"
              size="md"
              leftIcon={<LayoutDashboard className="w-4 h-4" />}
              className="w-full"
            >
              Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
