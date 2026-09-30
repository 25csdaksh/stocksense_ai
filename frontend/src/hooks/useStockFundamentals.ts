"use client";

import { useState, useEffect, useCallback } from "react";
import { stocksApi } from "@/lib/api/stocks";
import {
  FundamentalOverviewResponse,
  FinancialStatementsResponse,
  CompanyProfile,
} from "@/types";

export function useStockFundamentals(
  ticker: string,
  initialPeriod: "annual" | "quarterly" = "annual"
) {
  const [fundamentals, setFundamentals] = useState<FundamentalOverviewResponse | null>(null);
  const [incomeStatements, setIncomeStatements] = useState<FinancialStatementsResponse | null>(null);
  const [balanceSheets, setBalanceSheets] = useState<FinancialStatementsResponse | null>(null);
  const [cashFlowStatements, setCashFlowStatements] = useState<FinancialStatementsResponse | null>(null);
  const [profile, setProfile] = useState<CompanyProfile | null>(null);

  const [periodType, setPeriodType] = useState<"annual" | "quarterly">(initialPeriod);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState<boolean>(false);
  const [isUnavailable, setIsUnavailable] = useState<boolean>(false);

  const fetchFundamentals = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);
    setIsUnavailable(false);

    try {
      // 1. Fetch overview
      const data = await stocksApi.getFundamentalOverview(ticker);
      if (data && data.valuation) {
        setFundamentals(data);
        const isDemoStatus =
          data.data_status === "DEMO" || data.data_source === "DEMO";
        setIsDemo(isDemoStatus);
        setIsUnavailable(data.data_status === "UNAVAILABLE");
      }

      // 2. Fetch multi-period statements in parallel
      const [incomeRes, balanceRes, cashflowRes, profileRes] = await Promise.allSettled([
        stocksApi.getFinancialStatements(ticker, "income", periodType),
        stocksApi.getFinancialStatements(ticker, "balance_sheet", periodType),
        stocksApi.getFinancialStatements(ticker, "cash_flow", periodType),
        stocksApi.getCompanyProfile(ticker),
      ]);

      if (incomeRes.status === "fulfilled") {
        setIncomeStatements(incomeRes.value);
      }
      if (balanceRes.status === "fulfilled") {
        setBalanceSheets(balanceRes.value);
      }
      if (cashflowRes.status === "fulfilled") {
        setCashFlowStatements(cashflowRes.value);
      }
      if (profileRes.status === "fulfilled") {
        setProfile(profileRes.value);
      }
    } catch (err: any) {
      console.warn("Failed to fetch fundamentals from backend API:", err);
      setIsError(true);
      setError(err?.message || "Failed to retrieve company fundamentals");
    } finally {
      setIsLoading(false);
    }
  }, [ticker, periodType]);

  useEffect(() => {
    fetchFundamentals();
  }, [fetchFundamentals]);

  return {
    fundamentals,
    incomeStatements,
    balanceSheets,
    cashFlowStatements,
    profile,
    periodType,
    setPeriodType,
    isLoading,
    isError,
    error,
    isDemo,
    isUnavailable,
    refresh: fetchFundamentals,
  };
}
