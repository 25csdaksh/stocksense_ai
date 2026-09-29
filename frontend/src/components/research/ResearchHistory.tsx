"use client";

import React from "react";
import { ResearchSession } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { History, Plus, Trash2, Clock, Building2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ResearchHistoryProps {
  sessions: ResearchSession[];
  activeSessionId: string | null;
  onSelectSession: (session: ResearchSession) => void;
  onNewSession: () => void;
  onClearHistory: () => void;
}

export const ResearchHistory: React.FC<ResearchHistoryProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onClearHistory,
}) => {
  // Group sessions into Today, Yesterday, and Older
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000;

  const todaySessions = sessions.filter((s) => new Date(s.createdAt).getTime() >= today);
  const yesterdaySessions = sessions.filter(
    (s) => new Date(s.createdAt).getTime() >= yesterday && new Date(s.createdAt).getTime() < today
  );
  const olderSessions = sessions.filter((s) => new Date(s.createdAt).getTime() < yesterday);

  return (
    <Card className="border-border shadow-card bg-surface overflow-hidden">
      <CardHeader className="py-3 px-4 border-b border-border/60 bg-surface-subtle/50 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-primary" />
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-content">
            Research History
          </CardTitle>
        </div>

        <button
          onClick={onNewSession}
          className="p-1 rounded-lg text-primary hover:bg-primary-light/10 transition-colors"
          title="Start New Research"
          aria-label="Start New Research"
        >
          <Plus className="w-4 h-4" />
        </button>
      </CardHeader>

      <CardContent className="p-3 space-y-4 max-h-[600px] overflow-y-auto">
        {/* New Session Big Button */}
        <Button
          variant="outline"
          size="sm"
          onClick={onNewSession}
          className="w-full justify-start text-xs font-semibold border-dashed hover:border-primary hover:bg-primary-light/5"
          leftIcon={<Plus className="w-3.5 h-3.5 text-primary" />}
        >
          New Investigation
        </Button>

        {/* Sessions list */}
        {sessions.length > 0 ? (
          <div className="space-y-3">
            {/* Today */}
            {todaySessions.length > 0 && (
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-content-muted uppercase tracking-wider px-1">
                  Today
                </span>
                {todaySessions.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => onSelectSession(s)}
                    className={cn(
                      "p-2.5 rounded-xl border transition-all cursor-pointer space-y-1",
                      activeSessionId === s.id
                        ? "bg-primary-light/10 border-primary ring-1 ring-primary/20"
                        : "bg-surface hover:bg-surface-subtle border-border"
                    )}
                  >
                    <div className="flex items-center justify-between gap-1.5">
                      {s.ticker ? (
                        <Badge variant="primary" size="sm">
                          {s.ticker}
                        </Badge>
                      ) : (
                        <Badge variant="neutral" size="sm">
                          Market
                        </Badge>
                      )}
                      <span className="text-[10px] text-content-muted font-tabular">
                        {new Date(s.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-content line-clamp-2 leading-snug">
                      {s.title || s.lastQuery}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Yesterday */}
            {yesterdaySessions.length > 0 && (
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-content-muted uppercase tracking-wider px-1">
                  Yesterday
                </span>
                {yesterdaySessions.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => onSelectSession(s)}
                    className={cn(
                      "p-2.5 rounded-xl border transition-all cursor-pointer space-y-1",
                      activeSessionId === s.id
                        ? "bg-primary-light/10 border-primary ring-1 ring-primary/20"
                        : "bg-surface hover:bg-surface-subtle border-border"
                    )}
                  >
                    <div className="flex items-center justify-between gap-1.5">
                      {s.ticker ? (
                        <Badge variant="primary" size="sm">
                          {s.ticker}
                        </Badge>
                      ) : (
                        <Badge variant="neutral" size="sm">
                          Market
                        </Badge>
                      )}
                      <span className="text-[10px] text-content-muted">Yesterday</span>
                    </div>
                    <p className="text-xs font-semibold text-content line-clamp-2 leading-snug">
                      {s.title || s.lastQuery}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Older */}
            {olderSessions.length > 0 && (
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-content-muted uppercase tracking-wider px-1">
                  Older
                </span>
                {olderSessions.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => onSelectSession(s)}
                    className={cn(
                      "p-2.5 rounded-xl border transition-all cursor-pointer space-y-1",
                      activeSessionId === s.id
                        ? "bg-primary-light/10 border-primary ring-1 ring-primary/20"
                        : "bg-surface hover:bg-surface-subtle border-border"
                    )}
                  >
                    <div className="flex items-center justify-between gap-1.5">
                      {s.ticker ? (
                        <Badge variant="primary" size="sm">
                          {s.ticker}
                        </Badge>
                      ) : (
                        <Badge variant="neutral" size="sm">
                          Market
                        </Badge>
                      )}
                      <span className="text-[10px] text-content-muted">
                        {new Date(s.createdAt).toLocaleDateString([], { month: "short", day: "numeric" })}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-content line-clamp-2 leading-snug">
                      {s.title || s.lastQuery}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Clear History Button */}
            <div className="pt-2 border-t border-border-subtle flex justify-end">
              <button
                onClick={onClearHistory}
                className="text-[10px] text-content-muted hover:text-financial-loss flex items-center gap-1 transition-colors"
              >
                <Trash2 className="w-3 h-3" /> Clear History
              </button>
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-xs text-content-muted">
            No previous research queries found.
          </div>
        )}
      </CardContent>
    </Card>
  );
};
