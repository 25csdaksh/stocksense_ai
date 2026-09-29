import React from "react";
import { cn } from "@/lib/utils";
import { Layers } from "lucide-react";
import { Button } from "./Button";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center bg-surface rounded-xl border border-dashed border-border",
        className
      )}
    >
      <div className="p-3 rounded-full bg-surface-subtle text-content-muted mb-3">
        {icon || <Layers className="w-6 h-6" />}
      </div>
      <h4 className="text-sm font-bold text-content">{title}</h4>
      <p className="text-xs text-content-muted max-w-sm mt-1 mb-4 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="outline" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
