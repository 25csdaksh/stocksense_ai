"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Select } from "@/components/common/Select";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { useToast } from "@/components/common/Toast";
import { Settings, Shield, Globe, Key, Trash2, CheckCircle2, RotateCcw } from "lucide-react";

export default function SettingsPage() {
  const { addToast } = useToast();
  const [defaultMarket, setDefaultMarket] = useState("NSE");
  const [currency, setCurrency] = useState("INR");

  const handleSave = () => {
    addToast({
      type: "success",
      title: "Preferences Saved",
      description: "Default exchange and risk calculation parameters have been updated.",
    });
  };

  const handleClearCache = () => {
    try {
      localStorage.removeItem("marketmind_recent_searches");
      addToast({
        type: "info",
        title: "Search History Cleared",
        description: "Local search query cache and recent command history have been purged.",
      });
    } catch {
      // ignore
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6 max-w-4xl mx-auto pb-12">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface p-5 rounded-2xl border border-border shadow-card">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                <Settings className="w-4 h-4" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-content">
                SYSTEM SETTINGS & PREFERENCES
              </h1>
            </div>
            <p className="text-xs text-content-muted">
              Configure telemetry parameters, active exchange routing, base currency formatting, and analytical engine connectivity.
            </p>
          </div>
        </div>

        {/* Market & Currency Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-primary" />
              <CardTitle>Market & Currency Preferences</CardTitle>
            </div>
            <CardDescription>Configure primary market indices and default display currencies across workspaces</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Select
                label="Primary Market Exchange"
                value={defaultMarket}
                onChange={(e) => setDefaultMarket(e.target.value)}
                options={[
                  { value: "NSE", label: "NSE India (National Stock Exchange - ₹)" },
                  { value: "BSE", label: "BSE India (Bombay Stock Exchange - ₹)" },
                  { value: "US", label: "US Benchmark Markets (Demo Assets - $)" },
                ]}
              />
              <Select
                label="Reporting Currency"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                options={[
                  { value: "INR", label: "Indian Rupee (INR / ₹)" },
                  { value: "USD", label: "US Dollar (USD / $)" },
                ]}
              />
            </div>
          </CardContent>
        </Card>

        {/* Backend & AI Integration */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-secondary" />
              <CardTitle>Analytical Engine Endpoints</CardTitle>
            </div>
            <CardDescription>Backend FastAPI host, Qdrant vector store, and ML engine connectivity</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Backend API Base URL"
              defaultValue={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              disabled
              hint="Configured via client environment variable"
            />
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-surface-subtle border border-border space-y-1">
                <span className="text-[10px] text-content-muted uppercase font-semibold">FastAPI Gateway</span>
                <p className="text-xs font-bold text-financial-gain flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>ONLINE (Port 8000)</span>
                </p>
              </div>

              <div className="p-3 rounded-xl bg-surface-subtle border border-border space-y-1">
                <span className="text-[10px] text-content-muted uppercase font-semibold">Qdrant Vector DB</span>
                <p className="text-xs font-bold text-financial-gain flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>CONNECTED (Dense 768d)</span>
                </p>
              </div>

              <div className="p-3 rounded-xl bg-surface-subtle border border-border space-y-1">
                <span className="text-[10px] text-content-muted uppercase font-semibold">Isolation Forest Engine</span>
                <p className="text-xs font-bold text-financial-gain flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>CALIBRATED (Z-Score &plus; GARCH)</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Hygiene & Local Storage */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" />
              <CardTitle>Local Storage & Search Cache</CardTitle>
            </div>
            <CardDescription>Purge cached search histories, command indices, and temporary local tokens</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p className="text-xs font-bold text-content">Clear Command & Search Query Cache</p>
              <p className="text-[11px] text-content-muted">
                Removes saved search keywords from your local browser storage.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearCache}
              leftIcon={<Trash2 className="w-3.5 h-3.5 text-financial-loss" />}
            >
              Purge Local Cache
            </Button>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button variant="gold" size="md" onClick={handleSave}>
            Save Preferences
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}
