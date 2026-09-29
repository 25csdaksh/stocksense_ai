"use client";

import React from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Newspaper, ExternalLink } from "lucide-react";

export default function NewsPage() {
  const newsItems = [
    {
      id: "news-1",
      title: "RBI Signals Pro-Growth Monetary Stance amid Stable Inflation Outlook",
      summary: "Reserve Bank of India monetary policy committee commentary reinforces domestic macro resilience, boosting NIFTY Bank and large-cap financials.",
      source: "Economic Times",
      time: "45 mins ago",
      sentiment: "POSITIVE",
      tickers: ["HDFCBANK.NS", "ICICIBANK.NS", "^NSEBANK"],
    },
    {
      id: "news-2",
      title: "Tata Consultancy Services Signs $1.2B Enterprise AI Transformation Deal",
      summary: "TCS announces large-scale multi-year cloud and generative AI deployment across European banking clients.",
      source: "LiveMint",
      time: "2 hours ago",
      sentiment: "POSITIVE",
      tickers: ["TCS.NS", "^CNXIT"],
    },
    {
      id: "news-3",
      title: "Global Semiconductor Supply Chains Navigate Geopolitical Shifts",
      summary: "AI hardware demand sustains high momentum while enterprise server capex forecasts undergo quarterly re-evaluations.",
      source: "Reuters",
      time: "4 hours ago",
      sentiment: "NEUTRAL",
      tickers: ["NVDA", "AAPL"],
    },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-content">Financial News & Sentiment</h1>
            <Badge variant="primary" size="md">
              NLP Scored
            </Badge>
          </div>
          <p className="text-xs text-content-muted mt-0.5">
            Curated financial news feed with ticker tagging and sentiment polarity classification.
          </p>
        </div>

        <div className="space-y-4">
          {newsItems.map((item) => (
            <Card key={item.id} hoverable>
              <CardContent className="p-5 flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-bold text-content-muted">{item.source}</span>
                    <span className="text-[11px] text-content-muted">• {item.time}</span>
                    <Badge
                      variant={
                        item.sentiment === "POSITIVE"
                          ? "gain"
                          : item.sentiment === "NEGATIVE"
                          ? "loss"
                          : "neutral"
                      }
                      size="sm"
                    >
                      {item.sentiment}
                    </Badge>
                  </div>
                  <h3 className="text-base font-bold text-content hover:text-primary transition-colors cursor-pointer">
                    {item.title}
                  </h3>
                  <p className="text-xs text-content-muted leading-relaxed">{item.summary}</p>
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    {item.tickers.map((t) => (
                      <Badge key={t} variant="outline" size="sm">
                        {t}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="shrink-0 text-content-muted hover:text-primary cursor-pointer p-1">
                  <ExternalLink className="w-4 h-4" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
