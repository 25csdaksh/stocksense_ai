import React from "react";
import { cn } from "@/lib/utils";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular" | "card";
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = "rectangular",
  ...props
}) => {
  const variants: Record<"text" | "circular" | "rectangular" | "card", string> = {
    text: "h-4 w-full rounded",
    circular: "rounded-full aspect-square",
    rectangular: "rounded-lg",
    card: "rounded-xl h-32 w-full",
  };

  return (
    <div
      className={cn("skeleton-shimmer bg-surface-subtle", variants[variant], className)}
      {...props}
    />
  );
};
