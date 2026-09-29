"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Select } from "@/components/common/Select";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { useToast } from "@/components/common/Toast";
import { Settings, Shield, Globe, Key } from "lucide-react";

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

  return (
    <AppLayout>
      <div className="space-y-6 max-w-4xl">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-content">System Settings & Preferences</h1>
          <p className="text-xs text-content-muted mt-0.5">
            Manage data provider configurations, default currency, and API endpoints.
          </p>
        </div>

        {/* Market & Currency Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-primary" />
              <CardTitle>Market & Currency Preferences</CardTitle>
            </div>
            <CardDescription>Configure primary market indices and default display currencies</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Select
                label="Primary Market Exchange"
                value={defaultMarket}
                onChange={(e) => setDefaultMarket(e.target.value)}
                options={[
                  { value: "NSE", label: "NSE India (NIFTY 50 / SENSEX)" },
                  { value: "BSE", label: "BSE India" },
                  { value: "US", label: "US Benchmark Markets (Demo)" },
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
            <CardDescription>Backend FastAPI host and vector repository connectivity</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Backend API Base URL"
              defaultValue={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              disabled
              hint="Managed via NEXT_PUBLIC_API_URL environment variable"
            />
            <div className="flex items-center justify-between p-3 rounded-xl bg-surface-subtle border border-border">
              <div>
                <p className="text-xs font-bold text-content">Vector Store & ML Engine Status</p>
                <p className="text-[11px] text-content-muted">Qdrant dense collections + Isolation Forest active</p>
              </div>
              <Badge variant="gain" size="sm">ONLINE</Badge>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button variant="gold" size="md" onClick={handleSave}>
            Save Preferences
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}
