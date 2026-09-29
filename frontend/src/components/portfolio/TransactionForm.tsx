"use client";

import React, { useState } from "react";
import { Modal } from "@/components/common/Modal";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { AddTransactionPayload } from "@/lib/api/portfolio";
import { Plus, TrendingDown, TrendingUp, AlertCircle } from "lucide-react";

export interface TransactionFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: AddTransactionPayload, notes?: string) => Promise<{ success: boolean; error?: string }>;
}

const POPULAR_TICKERS = [
  "RELIANCE.NS",
  "TCS.NS",
  "HDFCBANK.NS",
  "INFY.NS",
  "ICICIBANK.NS",
  "BHARTIARTL.NS",
  "SBIN.NS",
  "TATAMOTORS.NS",
];

export const TransactionForm: React.FC<TransactionFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [ticker, setTicker] = useState<string>("");
  const [transactionType, setTransactionType] = useState<"BUY" | "SELL">("BUY");
  const [shares, setShares] = useState<string>("");
  const [price, setPrice] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const resetForm = () => {
    setTicker("");
    setTransactionType("BUY");
    setShares("");
    setPrice("");
    setNotes("");
    setErrorMsg(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanTicker = ticker.trim().toUpperCase();
    if (!cleanTicker) {
      setErrorMsg("Please provide a valid asset ticker symbol.");
      return;
    }

    const numShares = parseFloat(shares);
    if (isNaN(numShares) || numShares <= 0) {
      setErrorMsg("Shares quantity must be a positive number greater than 0.");
      return;
    }

    const numPrice = parseFloat(price);
    if (isNaN(numPrice) || numPrice < 0) {
      setErrorMsg("Execution price must be a valid non-negative number.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await onSubmit(
        {
          ticker: cleanTicker,
          shares: numShares,
          price: numPrice,
          transaction_type: transactionType,
        },
        notes.trim() || undefined
      );

      if (res.success) {
        handleClose();
      } else {
        setErrorMsg(res.error || "Failed to record transaction.");
      }
    } catch {
      setErrorMsg("An unexpected network error occurred while posting transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const estimatedTotal = (parseFloat(shares) || 0) * (parseFloat(price) || 0);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Record Portfolio Transaction"
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-2">
        {errorMsg && (
          <div className="p-3 bg-financial-loss-bg border border-financial-loss/30 rounded-xl text-xs text-financial-loss flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Transaction Type Selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-content block">Order Side</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setTransactionType("BUY")}
              className={`p-2.5 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                transactionType === "BUY"
                  ? "bg-primary text-white border-primary shadow-xs"
                  : "bg-surface border-border text-content-muted hover:text-content hover:bg-surface-subtle"
              }`}
            >
              <TrendingDown className="w-4 h-4 text-emerald-400" />
              BUY (Acquisition)
            </button>
            <button
              type="button"
              onClick={() => setTransactionType("SELL")}
              className={`p-2.5 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                transactionType === "SELL"
                  ? "bg-financial-loss text-white border-financial-loss shadow-xs"
                  : "bg-surface border-border text-content-muted hover:text-content hover:bg-surface-subtle"
              }`}
            >
              <TrendingUp className="w-4 h-4 text-rose-300" />
              SELL (Disposition)
            </button>
          </div>
        </div>

        {/* Ticker Input */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-content block">Ticker Symbol</label>
          <Input
            placeholder="e.g. RELIANCE.NS, TCS.NS"
            value={ticker}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTicker(e.target.value.toUpperCase())}
            required
            className="font-mono uppercase font-bold"
          />
          {/* Quick Select Chips */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {POPULAR_TICKERS.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTicker(t)}
                className="px-2 py-0.5 text-[10px] font-mono font-medium rounded border border-border bg-surface-subtle hover:bg-primary-light hover:text-primary hover:border-primary/30 transition-all text-content-muted"
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Quantity and Price Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-content block">Quantity (Shares)</label>
            <Input
              type="number"
              step="any"
              min="0.0001"
              placeholder="e.g. 50"
              value={shares}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setShares(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-content block">Execution Price (₹)</label>
            <Input
              type="number"
              step="any"
              min="0.01"
              placeholder="e.g. 2840.50"
              value={price}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPrice(e.target.value)}
              required
            />
          </div>
        </div>

        {/* Notes / Rationale */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-content block">
            Execution Notes / Strategy Rationale <span className="text-content-muted font-normal">(Optional)</span>
          </label>
          <Input
            placeholder="e.g. Long-term core compounding rebalance"
            value={notes}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNotes(e.target.value)}
          />
        </div>

        {/* Estimated Value Banner */}
        {estimatedTotal > 0 && (
          <div className="p-3 bg-surface-subtle rounded-xl border border-border flex items-center justify-between text-xs">
            <span className="text-content-muted font-medium">Estimated Gross Value:</span>
            <span className="font-bold text-content font-tabular text-sm">
              ₹{estimatedTotal.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-2 pt-3 border-t border-border">
          <Button type="button" variant="ghost" size="sm" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="gold"
            size="sm"
            disabled={isSubmitting}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            {isSubmitting ? "Executing Trade..." : "Post Transaction"}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
