"use client";

import React, { useState, useMemo } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatCurrency } from "@/lib/utils";
import { PortfolioTransaction } from "@/types";
import {
  History,
  TrendingUp,
  TrendingDown,
  ChevronDown,
  Search,
} from "lucide-react";

export interface TransactionHistoryProps {
  transactions: PortfolioTransaction[];
  onAddTransaction: () => void;
}

type TxFilter = "ALL" | "BUY" | "SELL" | "DIVIDEND";

export const TransactionHistory: React.FC<TransactionHistoryProps> = ({
  transactions,
  onAddTransaction,
}) => {
  const [filter, setFilter] = useState<TxFilter>("ALL");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [search, setSearch] = useState<string>("");

  const filteredTransactions = useMemo(() => {
    let list = [...transactions];

    if (filter !== "ALL") {
      list = list.filter((t) => t.transaction_type === filter);
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (t) =>
          t.ticker.toLowerCase().includes(q) ||
          (t.company_name && t.company_name.toLowerCase().includes(q)) ||
          (t.notes && t.notes.toLowerCase().includes(q))
      );
    }

    list.sort((a, b) => {
      const timeA = new Date(a.executed_at).getTime();
      const timeB = new Date(b.executed_at).getTime();
      return sortOrder === "desc" ? timeB - timeA : timeA - timeB;
    });

    return list;
  }, [transactions, filter, search, sortOrder]);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center gap-2">
              <History className="w-4 h-4 text-primary" />
              Transaction Activity &amp; Trade Ledger
            </CardTitle>
            <Badge variant="neutral" size="sm">
              {transactions.length} Executions
            </Badge>
          </div>
          <CardDescription>
            Audit log of all portfolio transactions, buy/sell orders, and executed cost bases.
          </CardDescription>
        </div>

        {/* Filter and Search Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative w-full sm:w-48">
            <Search className="w-3.5 h-3.5 text-content-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search trades..."
              value={search}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
              className="w-full pl-8 pr-2.5 py-1 text-xs rounded-lg border border-border bg-surface-subtle focus:bg-surface focus:outline-none focus:ring-1 focus:ring-primary text-content"
            />
          </div>

          <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border">
            {(["ALL", "BUY", "SELL", "DIVIDEND"] as TxFilter[]).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-0.5 text-[11px] font-semibold rounded transition-all ${
                  filter === f
                    ? "bg-primary text-white shadow-xs"
                    : "text-content-muted hover:text-content hover:bg-surface"
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <button
            onClick={() => setSortOrder((prev) => (prev === "desc" ? "asc" : "desc"))}
            title="Toggle Date Sorting"
            className="p-1.5 rounded-lg border border-border text-content-muted hover:text-content hover:bg-surface-subtle text-xs flex items-center gap-1"
          >
            <ChevronDown className="w-3.5 h-3.5" />
            <span className="text-[10px] hidden sm:inline">{sortOrder === "desc" ? "Newest" : "Oldest"}</span>
          </button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {filteredTransactions.length === 0 ? (
          <div className="p-8 text-center text-xs text-content-muted">
            No transactions match the selected filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-surface-subtle/50 text-content-muted font-semibold">
                  <th className="p-3.5 pl-4">Date &amp; Time</th>
                  <th className="p-3.5">Asset</th>
                  <th className="p-3.5 text-center">Type</th>
                  <th className="p-3.5 text-right">Shares</th>
                  <th className="p-3.5 text-right">Price</th>
                  <th className="p-3.5 text-right">Fees / Tax</th>
                  <th className="p-3.5 pr-4 text-right">Total Consideration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredTransactions.map((tx) => {
                  const isBuy = tx.transaction_type === "BUY";
                  const isSell = tx.transaction_type === "SELL";
                  const dateObj = new Date(tx.executed_at);
                  const dateStr = dateObj.toLocaleDateString("en-IN", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  });
                  const timeStr = dateObj.toLocaleTimeString("en-IN", {
                    hour: "2-digit",
                    minute: "2-digit",
                  });

                  return (
                    <tr key={tx.id} className="hover:bg-surface-subtle/60 transition-colors">
                      {/* Date & Time */}
                      <td className="p-3.5 pl-4 text-content font-medium whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <span>{dateStr}</span>
                          <span className="text-[10px] text-content-muted">{timeStr}</span>
                        </div>
                      </td>

                      {/* Asset */}
                      <td className="p-3.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-content">{tx.ticker}</span>
                          {tx.company_name && (
                            <span className="text-[11px] text-content-muted truncate max-w-[140px] hidden md:inline">
                              {tx.company_name}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Type Badge */}
                      <td className="p-3.5 text-center">
                        <Badge
                          variant={isBuy ? "gain" : isSell ? "loss" : "secondary"}
                          size="sm"
                          className="font-bold text-[10px] uppercase tracking-wider inline-flex items-center gap-1"
                        >
                          {isBuy ? (
                            <TrendingDown className="w-3 h-3 text-financial-gain" />
                          ) : (
                            <TrendingUp className="w-3 h-3 text-financial-loss" />
                          )}
                          {tx.transaction_type}
                        </Badge>
                      </td>

                      {/* Shares */}
                      <td className="p-3.5 text-right font-tabular text-content font-semibold">
                        {tx.shares}
                      </td>

                      {/* Price */}
                      <td className="p-3.5 text-right font-tabular text-content-muted">
                        {formatCurrency(tx.price, "INR")}
                      </td>

                      {/* Fees */}
                      <td className="p-3.5 text-right font-tabular text-content-muted text-[11px]">
                        {tx.fees ? formatCurrency(tx.fees, "INR") : "₹0.00"}
                      </td>

                      {/* Total Consideration */}
                      <td className="p-3.5 pr-4 text-right font-tabular font-bold text-content">
                        {formatCurrency(tx.total_value, "INR")}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
