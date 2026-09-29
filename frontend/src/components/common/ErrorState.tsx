import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Failed to load market intelligence",
  message = "An unexpected error occurred while communicating with the analytical server.",
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center bg-financial-loss-bg/30 rounded-xl border border-financial-loss/20",
        className
      )}
    >
      <div className="p-3 rounded-full bg-financial-loss-bg text-financial-loss mb-3">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-bold text-content">{title}</h4>
      <p className="text-xs text-content-muted max-w-sm mt-1 mb-4 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Try Again
        </Button>
      )}
    </div>
  );
};
