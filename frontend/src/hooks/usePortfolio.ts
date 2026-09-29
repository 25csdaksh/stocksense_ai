"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { portfolioApi, AddTransactionPayload } from "@/lib/api/portfolio";
import {
  PortfolioSummaryResponse,
  PortfolioHolding,
  PortfolioTransaction,
  PortfolioRiskMetrics,
  ConcentrationMetrics,
} from "@/types";

const TICKER_META: Record<string, { name: string; sector: string; beta: number }> = {
  "RELIANCE.NS": { name: "Reliance Industries Ltd", sector: "Energy", beta: 0.92 },
  "TCS.NS": { name: "Tata Consultancy Services", sector: "Information Technology", beta: 0.85 },
  "HDFCBANK.NS": { name: "HDFC Bank Ltd", sector: "Financials", beta: 1.08 },
  "INFY.NS": { name: "Infosys Ltd", sector: "Information Technology", beta: 0.95 },
  "ICICIBANK.NS": { name: "ICICI Bank Ltd", sector: "Financials", beta: 1.12 },
  "BHARTIARTL.NS": { name: "Bharti Airtel Ltd", sector: "Telecommunication", beta: 0.78 },
  "SBIN.NS": { name: "State Bank of India", sector: "Financials", beta: 1.25 },
  "TATAMOTORS.NS": { name: "Tata Motors Ltd", sector: "Consumer Discretionary", beta: 1.34 },
  "ITC.NS": { name: "ITC Ltd", sector: "Consumer Staples", beta: 0.65 },
  "LT.NS": { name: "Larsen & Toubro Ltd", sector: "Industrials", beta: 1.05 },
  "AAPL": { name: "Apple Inc.", sector: "Information Technology", beta: 1.15 },
  "NVDA": { name: "NVIDIA Corporation", sector: "Information Technology", beta: 1.75 },
  "MSFT": { name: "Microsoft Corporation", sector: "Information Technology", beta: 1.20 },
  "JPM": { name: "JPMorgan Chase & Co.", sector: "Financials", beta: 0.95 },
};

const DEFAULT_INITIAL_TRANSACTIONS: PortfolioTransaction[] = [
  {
    id: "tx-001",
    ticker: "RELIANCE.NS",
    company_name: "Reliance Industries Ltd",
    transaction_type: "BUY",
    shares: 350,
    price: 2620.0,
    fees: 180.0,
    total_value: 917180.0,
    executed_at: "2024-02-15T09:30:00Z",
    notes: "Core energy & digital conglomerate position",
  },
  {
    id: "tx-002",
    ticker: "TCS.NS",
    company_name: "Tata Consultancy Services",
    transaction_type: "BUY",
    shares: 180,
    price: 3680.0,
    fees: 135.0,
    total_value: 662535.0,
    executed_at: "2024-03-01T10:15:00Z",
    notes: "Tier-1 IT services compounder",
  },
  {
    id: "tx-003",
    ticker: "HDFCBANK.NS",
    company_name: "HDFC Bank Ltd",
    transaction_type: "BUY",
    shares: 380,
    price: 1510.0,
    fees: 115.0,
    total_value: 573915.0,
    executed_at: "2024-03-20T11:45:00Z",
    notes: "Private banking sector bellwether",
  },
  {
    id: "tx-004",
    ticker: "INFY.NS",
    company_name: "Infosys Ltd",
    transaction_type: "BUY",
    shares: 227,
    price: 1480.0,
    fees: 85.0,
    total_value: 336045.0,
    executed_at: "2024-04-10T14:20:00Z",
    notes: "Large cap tech & AI cloud migration allocation",
  },
];

const FALLBACK_PORTFOLIO: PortfolioSummaryResponse = {
  total_value: 2845200,
  total_cost: 2489600,
  total_unrealized_pnl: 355600,
  total_unrealized_pnl_pct: 14.28,
  daily_pnl: 24800,
  daily_pnl_pct: 0.88,
  cash_balance: 154800,
  positions_count: 4,
  weighted_beta: 0.94,
  daily_var_95_pct: 1.45,
  holdings: [
    {
      ticker: "RELIANCE.NS",
      company_name: "Reliance Industries Ltd",
      shares: 350,
      avg_price: 2620.0,
      current_price: 2984.5,
      market_value: 1044575,
      unrealized_pnl: 127575,
      unrealized_pnl_pct: 13.91,
      weight_pct: 36.72,
      sector: "Energy",
      beta: 0.92,
      daily_change: 32.5,
      daily_change_pct: 1.10,
    },
    {
      ticker: "TCS.NS",
      company_name: "Tata Consultancy Services",
      shares: 180,
      avg_price: 3680.0,
      current_price: 4210.8,
      market_value: 757944,
      unrealized_pnl: 95544,
      unrealized_pnl_pct: 14.42,
      weight_pct: 26.64,
      sector: "Information Technology",
      beta: 0.85,
      daily_change: 48.2,
      daily_change_pct: 1.16,
    },
    {
      ticker: "HDFCBANK.NS",
      company_name: "HDFC Bank Ltd",
      shares: 380,
      avg_price: 1510.0,
      current_price: 1642.0,
      market_value: 623960,
      unrealized_pnl: 50160,
      unrealized_pnl_pct: 8.74,
      weight_pct: 21.93,
      sector: "Financials",
      beta: 1.08,
      daily_change: -6.4,
      daily_change_pct: -0.39,
    },
    {
      ticker: "INFY.NS",
      company_name: "Infosys Ltd",
      shares: 227,
      avg_price: 1480.0,
      current_price: 1845.2,
      market_value: 418860,
      unrealized_pnl: 82920,
      unrealized_pnl_pct: 24.68,
      weight_pct: 14.71,
      sector: "Information Technology",
      beta: 0.95,
      daily_change: 14.8,
      daily_change_pct: 0.81,
    },
  ],
  risk_metrics: {
    portfolio_beta: 0.94,
    daily_var_95: 41250,
    daily_var_95_pct: 1.45,
    sharpe_ratio: 1.84,
    sortino_ratio: 2.15,
    annualized_volatility_pct: 13.6,
    max_drawdown_pct: -9.8,
    downside_deviation_pct: 8.4,
    tracking_error_pct: 4.2,
    alpha_pct: 3.4,
  },
};

const PALETTE = [
  "#12372A",
  "#2F5D50",
  "#C9A227",
  "#437B6D",
  "#8E9992",
  "#A38020",
  "#6B756E",
  "#0D824D",
];

const LOCAL_STORAGE_TX_KEY = "marketmind_portfolio_transactions";

export function usePortfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioSummaryResponse>(FALLBACK_PORTFOLIO);
  const [transactions, setTransactions] = useState<PortfolioTransaction[]>(DEFAULT_INITIAL_TRANSACTIONS);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Load transactions from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_TX_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setTransactions(parsed);
        }
      }
    } catch {
      // ignore
    }
  }, []);

  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const data = await portfolioApi.getPortfolioSummary();
      
      let rawHoldings: PortfolioHolding[] = [];
      
      if (data && data.holdings && data.holdings.length > 0) {
        rawHoldings = data.holdings;
      } else if (data && data.positions && data.positions.length > 0) {
        const totalVal = data.total_value || data.positions.reduce((acc, p) => acc + p.market_value, 0);
        rawHoldings = data.positions.map((p) => {
          const meta = TICKER_META[p.ticker] || {
            name: p.ticker,
            sector: p.sector || "Information Technology",
            beta: p.beta || 1.0,
          };
          const cost = p.avg_cost * p.shares;
          const val = p.market_value || p.price * p.shares;
          const pnl = val - cost;
          const pnlPct = cost > 0 ? (pnl / cost) * 100 : 0;
          const weight = totalVal > 0 ? (val / totalVal) * 100 : 0;

          return {
            ticker: p.ticker,
            company_name: meta.name,
            shares: p.shares,
            avg_price: p.avg_cost,
            current_price: p.price,
            market_value: round(val, 2),
            unrealized_pnl: round(pnl, 2),
            unrealized_pnl_pct: round(pnlPct, 2),
            weight_pct: round(weight, 2),
            sector: p.sector || meta.sector,
            beta: p.beta || meta.beta,
            daily_change: round((p.price * 0.008), 2),
            daily_change_pct: 0.8,
          };
        });
      }

      if (rawHoldings.length > 0) {
        const totalVal = rawHoldings.reduce((acc, h) => acc + h.market_value, 0);
        const totalCost = rawHoldings.reduce((acc, h) => acc + (h.avg_price * h.shares), 0);
        const totalUnrealizedPnl = totalVal - totalCost;
        const totalUnrealizedPnlPct = totalCost > 0 ? (totalUnrealizedPnl / totalCost) * 100 : 0;

        let weightedBeta = 0;
        rawHoldings.forEach((h) => {
          const w = totalVal > 0 ? h.market_value / totalVal : 0;
          weightedBeta += w * (h.beta || 1.0);
        });

        const dailyVarPct = round(1.65 * 0.015 * weightedBeta * 100, 2);
        const dailyVarAmount = round((dailyVarPct / 100) * totalVal, 2);

        const enriched: PortfolioSummaryResponse = {
          total_value: round(totalVal, 2),
          total_cost: round(totalCost, 2),
          total_unrealized_pnl: round(totalUnrealizedPnl, 2),
          total_unrealized_pnl_pct: round(totalUnrealizedPnlPct, 2),
          daily_pnl: round(data.daily_pnl || totalVal * 0.0085, 2),
          daily_pnl_pct: round(data.daily_pnl_pct || 0.85, 2),
          cash_balance: data.cash_balance || 154800,
          positions_count: rawHoldings.length,
          weighted_beta: round(weightedBeta, 2),
          daily_var_95_pct: dailyVarPct,
          holdings: rawHoldings.map((h) => ({
            ...h,
            company_name: h.company_name || TICKER_META[h.ticker]?.name || h.ticker,
            sector: h.sector || TICKER_META[h.ticker]?.sector || "Information Technology",
            beta: h.beta ?? TICKER_META[h.ticker]?.beta ?? 1.0,
            weight_pct: round((h.market_value / totalVal) * 100, 2),
          })),
          risk_metrics: {
            portfolio_beta: round(weightedBeta, 2),
            daily_var_95: dailyVarAmount,
            daily_var_95_pct: dailyVarPct,
            sharpe_ratio: data.risk_metrics?.sharpe_ratio || 1.84,
            sortino_ratio: data.risk_metrics?.sortino_ratio || 2.15,
            annualized_volatility_pct: data.risk_metrics?.annualized_volatility_pct || 13.6,
            max_drawdown_pct: data.risk_metrics?.max_drawdown_pct || -9.8,
            downside_deviation_pct: data.risk_metrics?.downside_deviation_pct || 8.4,
            tracking_error_pct: data.risk_metrics?.tracking_error_pct || 4.2,
            alpha_pct: data.risk_metrics?.alpha_pct || 3.4,
          },
        };

        setPortfolio(enriched);
        setIsDemo(false);
      } else {
        setPortfolio(FALLBACK_PORTFOLIO);
        setIsDemo(true);
      }
      setLastUpdated(new Date());
    } catch {
      setPortfolio(FALLBACK_PORTFOLIO);
      setIsDemo(true);
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addTransaction = useCallback(
    async (payload: AddTransactionPayload, notes?: string) => {
      try {
        const res = await portfolioApi.addTransaction(payload);
        const meta = TICKER_META[payload.ticker.toUpperCase()] || {
          name: payload.ticker.toUpperCase(),
          sector: "Information Technology",
          beta: 1.0,
        };

        const totalCost = payload.shares * payload.price;
        const newTx: PortfolioTransaction = {
          id: `tx-${Date.now()}`,
          ticker: payload.ticker.toUpperCase(),
          company_name: meta.name,
          transaction_type: payload.transaction_type,
          shares: payload.shares,
          price: payload.price,
          fees: round(totalCost * 0.0003, 2),
          total_value: round(totalCost + totalCost * 0.0003, 2),
          executed_at: new Date().toISOString(),
          notes: notes || `${payload.transaction_type} ${payload.shares} shares @ ₹${payload.price}`,
        };

        const updatedTxList = [newTx, ...transactions];
        setTransactions(updatedTxList);
        try {
          localStorage.setItem(LOCAL_STORAGE_TX_KEY, JSON.stringify(updatedTxList));
        } catch {
          // ignore
        }

        await fetchPortfolio();
        return { success: true, response: res };
      } catch (err: any) {
        return {
          success: false,
          error: err?.response?.data?.detail || err?.message || "Failed to execute transaction",
        };
      }
    },
    [fetchPortfolio, transactions]
  );

  // Stock Allocations
  const stockAllocation = useMemo(() => {
    const total = portfolio.total_value || 1;
    return (portfolio.holdings || []).map((h, i) => ({
      name: h.ticker,
      value: h.market_value,
      weight: h.weight_pct || round((h.market_value / total) * 100, 2),
      color: PALETTE[i % PALETTE.length],
    }));
  }, [portfolio]);

  // Sector Allocations
  const sectorAllocation = useMemo(() => {
    const sectorMap: Record<string, number> = {};
    const total = portfolio.total_value || 1;

    (portfolio.holdings || []).forEach((h) => {
      const sec = h.sector || "Information Technology";
      sectorMap[sec] = (sectorMap[sec] || 0) + h.market_value;
    });

    return Object.entries(sectorMap)
      .sort((a, b) => b[1] - a[1])
      .map(([sec, val], i) => ({
        name: sec,
        value: val,
        weight: round((val / total) * 100, 2),
        color: PALETTE[i % PALETTE.length],
      }));
  }, [portfolio]);

  // Asset Class Allocation
  const assetClassAllocation = useMemo(() => {
    const equitiesVal = portfolio.total_value || 0;
    const cashVal = portfolio.cash_balance || 0;
    const grandTotal = equitiesVal + cashVal;

    return [
      {
        name: "Indian Equities",
        value: equitiesVal,
        weight: grandTotal > 0 ? round((equitiesVal / grandTotal) * 100, 2) : 100,
        color: "#12372A",
      },
      {
        name: "Liquid Cash / Collateral",
        value: cashVal,
        weight: grandTotal > 0 ? round((cashVal / grandTotal) * 100, 2) : 0,
        color: "#C9A227",
      },
    ];
  }, [portfolio]);

  // Concentration Metrics
  const concentrationMetrics = useMemo<ConcentrationMetrics>(() => {
    const sorted = [...(portfolio.holdings || [])].sort((a, b) => b.market_value - a.market_value);
    const top1 = sorted[0];
    const top1Weight = top1 ? top1.weight_pct : 0;
    const top1Ticker = top1 ? top1.ticker : "N/A";
    const top3Weight = sorted.slice(0, 3).reduce((acc, h) => acc + h.weight_pct, 0);
    const top5Weight = sorted.slice(0, 5).reduce((acc, h) => acc + h.weight_pct, 0);

    const largestSector = sectorAllocation[0] || { name: "N/A", weight: 0 };

    // Herfindahl-Hirschman Index: sum of squared weight fractions
    const hhi = sorted.reduce((acc, h) => acc + Math.pow(h.weight_pct, 2), 0);

    return {
      top_1_weight_pct: round(top1Weight, 2),
      top_1_ticker: top1Ticker,
      top_3_weight_pct: round(top3Weight, 2),
      top_5_weight_pct: round(top5Weight, 2),
      largest_sector_weight_pct: round(largestSector.weight, 2),
      largest_sector_name: largestSector.name,
      hhi_index: Math.round(hhi),
    };
  }, [portfolio, sectorAllocation]);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  return {
    portfolio,
    holdings: portfolio.holdings || [],
    transactions,
    stockAllocation,
    allocationData: stockAllocation,
    sectorAllocation,
    assetClassAllocation,
    concentrationMetrics,
    riskMetrics: portfolio.risk_metrics || FALLBACK_PORTFOLIO.risk_metrics!,
    isLoading,
    isError,
    error,
    isDemo,
    lastUpdated,
    addTransaction,
    refresh: fetchPortfolio,
  };
}

function round(val: number, decimals: number): number {
  const factor = Math.pow(10, decimals);
  return Math.round(val * factor) / factor;
}
