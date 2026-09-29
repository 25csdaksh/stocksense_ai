import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "primary" | "secondary" | "gold" | "gain" | "loss" | "neutral" | "outline";
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = "neutral",
  size = "sm",
  children,
  ...props
}) => {
  const baseStyles = "inline-flex items-center font-medium rounded-full select-none";

  const variants = {
    primary: "bg-primary-light text-primary border border-primary/20",
    secondary: "bg-secondary-light text-secondary border border-secondary/20",
    gold: "bg-accent-light text-accent-dark border border-accent/30 font-semibold",
    gain: "bg-financial-gain-bg text-financial-gain border border-financial-gain/20",
    loss: "bg-financial-loss-bg text-financial-loss border border-financial-loss/20",
    neutral: "bg-surface-subtle text-content-muted border border-border",
    outline: "bg-transparent text-content border border-border",
  };

  const sizes = {
    sm: "text-[11px] px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5",
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
};
