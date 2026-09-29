"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { cn } from "@/lib/utils";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export type ToastType = "success" | "error" | "info";

export interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

interface ToastContextType {
  toasts: ToastItem[];
  addToast: (toast: Omit<ToastItem, "id">) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children?: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    ({ type, title, description, duration = 4000 }: Omit<ToastItem, "id">) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newToast: ToastItem = { id, type, title, description, duration };

      setToasts((prev) => [...prev, newToast]);

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast]
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "pointer-events-auto flex items-start gap-3 p-4 rounded-xl border shadow-modal bg-surface transition-all animate-in slide-in-from-bottom-2 duration-200",
              toast.type === "success" && "border-financial-gain/30 bg-surface",
              toast.type === "error" && "border-financial-loss/30 bg-surface",
              toast.type === "info" && "border-secondary/30 bg-surface"
            )}
          >
            <div className="shrink-0 mt-0.5">
              {toast.type === "success" && <CheckCircle2 className="w-4 h-4 text-financial-gain" />}
              {toast.type === "error" && <AlertCircle className="w-4 h-4 text-financial-loss" />}
              {toast.type === "info" && <Info className="w-4 h-4 text-secondary" />}
            </div>
            <div className="flex-1 min-w-0">
              <h5 className="text-xs font-bold text-content">{toast.title}</h5>
              {toast.description && (
                <p className="text-xs text-content-muted mt-0.5">{toast.description}</p>
              )}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="shrink-0 text-content-muted hover:text-content p-0.5 rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
