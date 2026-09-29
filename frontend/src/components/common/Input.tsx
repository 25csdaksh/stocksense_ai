import React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, leftIcon, rightIcon, id, type = "text", ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold text-content/90 tracking-wide">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-content-muted">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            type={type}
            className={cn(
              "w-full rounded-lg border bg-surface px-3.5 py-2 text-sm text-content placeholder:text-content-muted/60 transition-all",
              "focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary",
              error ? "border-financial-loss focus:border-financial-loss focus:ring-financial-loss/20" : "border-border",
              leftIcon ? "pl-9" : "",
              rightIcon ? "pr-9" : "",
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 flex items-center pointer-events-none text-content-muted">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="text-xs text-financial-loss font-medium mt-0.5">{error}</p>}
        {!error && hint && <p className="text-xs text-content-muted mt-0.5">{hint}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
