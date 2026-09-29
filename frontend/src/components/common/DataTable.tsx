import React from "react";
import { cn } from "@/lib/utils";

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T, index: number) => React.ReactNode;
  align?: "left" | "center" | "right";
  className?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T, index: number) => string;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  isLoading = false,
  emptyMessage = "No financial records found.",
  onRowClick,
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn("w-full overflow-x-auto border border-border rounded-xl bg-surface", className)}>
      <table className="w-full text-left text-sm border-collapse">
        <thead>
          <tr className="border-b border-border bg-surface-subtle/70">
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn(
                  "py-3 px-4 text-xs font-semibold uppercase tracking-wider text-content-muted/90",
                  col.align === "right" && "text-right",
                  col.align === "center" && "text-center",
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-subtle">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, rIdx) => (
              <tr key={`loading-${rIdx}`} className="animate-pulse">
                {columns.map((col) => (
                  <td key={col.key} className="py-3.5 px-4">
                    <div className="h-4 bg-surface-subtle rounded w-3/4" />
                  </td>
                ))}
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-8 text-center text-xs text-content-muted">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr
                key={keyExtractor(item, idx)}
                onClick={() => onRowClick?.(item)}
                className={cn(
                  "transition-colors hover:bg-surface-subtle/50",
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn(
                      "py-3.5 px-4 text-content",
                      col.align === "right" && "text-right font-tabular",
                      col.align === "center" && "text-center",
                      col.className
                    )}
                  >
                    {col.render
                      ? col.render(item, idx)
                      : String((item as Record<string, unknown>)[col.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
