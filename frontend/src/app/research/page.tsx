"use client";

import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { useResearch } from "@/hooks/useResearch";
import { useResearchHistory } from "@/hooks/useResearchHistory";
import {
  ResearchHeader,
  ResearchComposer,
  ResearchExecution,
  ResearchResult,
  ResearchEvidencePanel,
  ResearchContextPanel,
  ResearchHistory,
  ResearchReportView,
  ResearchLoadingState,
} from "@/components/research";
import { CitationItem, ResearchSession } from "@/types";
import { Tabs } from "@/components/common/Tabs";
import { Brain, History, BookOpen, Layers, ShieldAlert } from "lucide-react";

export default function ResearchPage() {
  const searchParams = useSearchParams();
  const urlTicker = searchParams.get("ticker") || null;
  const urlQuery = searchParams.get("q") || "";

  const {
    selectedTicker,
    setSelectedTicker,
    mode,
    setMode,
    messages,
    pipelineNodes,
    citations,
    contextFlags,
    isProcessing,
    isReportMode,
    setIsReportMode,
    error,
    executeResearch,
    loadSession,
    resetSession,
  } = useResearch(urlTicker);

  const {
    sessions,
    activeSessionId,
    setActiveSessionId,
    saveSession,
    deleteSession,
    clearHistory,
  } = useResearchHistory();

  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [mobileTab, setMobileTab] = useState<"research" | "history" | "evidence">("research");

  // Handle URL query preload
  useEffect(() => {
    if (urlQuery && messages.length === 0) {
      executeResearch(urlQuery, urlTicker || undefined);
    }
  }, [urlQuery, urlTicker, executeResearch, messages.length]);

  // Handle saving completed research into session history
  useEffect(() => {
    if (messages.length > 0 && !isProcessing) {
      const lastUser = [...messages].reverse().find((m) => m.role === "user");
      const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");
      if (lastUser && lastAssistant) {
        const sessionTitle =
          lastUser.content.length > 45 ? `${lastUser.content.slice(0, 45)}...` : lastUser.content;
        const newSession: ResearchSession = {
          id: `sess_${Date.now()}`,
          title: sessionTitle,
          ticker: selectedTicker,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages,
          lastQuery: lastUser.content,
        };
        saveSession(newSession);
      }
    }
  }, [messages, isProcessing, saveSession, selectedTicker]);

  const handleSelectSessionFromHistory = (session: ResearchSession) => {
    setActiveSessionId(session.id);
    loadSession(session);
    setMobileTab("research");
  };

  const handleStartNewSession = () => {
    resetSession();
    setSelectedTicker(null);
    setMobileTab("research");
  };

  // Get the most recent assistant message
  const latestAssistantMessage = [...messages].reverse().find((m) => m.role === "assistant");

  const mobileTabs = [
    { id: "research", label: "Research Terminal", icon: <Brain className="w-4 h-4" /> },
    { id: "evidence", label: `Evidence (${citations.length})`, icon: <BookOpen className="w-4 h-4" /> },
    { id: "history", label: `History (${sessions.length})`, icon: <History className="w-4 h-4" /> },
  ];

  return (
    <AppLayout>
      <div className="space-y-6 pb-12">
        {/* Terminal Header */}
        <ResearchHeader
          selectedTicker={selectedTicker}
          onSelectTicker={setSelectedTicker}
          mode={mode}
          onSelectMode={setMode}
          isReportMode={isReportMode}
          onToggleReportMode={() => setIsReportMode(!isReportMode)}
          onResetSession={handleStartNewSession}
        />

        {/* Mobile View Switcher Tabs (Visible on < 1024px) */}
        <div className="block lg:hidden">
          <Tabs
            tabs={mobileTabs}
            activeTab={mobileTab}
            onChange={(tabId) => setMobileTab(tabId as "research" | "history" | "evidence")}
          />
        </div>

        {/* Formal Report View Mode */}
        {isReportMode && latestAssistantMessage ? (
          <ResearchReportView
            message={latestAssistantMessage}
            onClose={() => setIsReportMode(false)}
          />
        ) : (
          /* Institutional 3-Column Workstation Grid */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Research History (3 Cols on Desktop) */}
            <div
              className={`lg:col-span-3 space-y-6 ${
                mobileTab !== "history" ? "hidden lg:block" : "block"
              }`}
            >
              <ResearchHistory
                sessions={sessions}
                activeSessionId={activeSessionId}
                onSelectSession={handleSelectSessionFromHistory}
                onNewSession={handleStartNewSession}
                onClearHistory={clearHistory}
              />
            </div>

            {/* Center Column: Query Composer, Pipeline DAG & Results (6 Cols on Desktop) */}
            <div
              className={`lg:col-span-6 space-y-6 ${
                mobileTab !== "research" ? "hidden lg:block" : "block"
              }`}
            >
              {/* Research Composer Box */}
              <ResearchComposer
                selectedTicker={selectedTicker}
                onSelectTicker={setSelectedTicker}
                onSubmit={(q) => executeResearch(q)}
                isProcessing={isProcessing}
                initialQuery={urlQuery}
              />

              {/* Multi-Agent Pipeline Visualization */}
              <ResearchExecution nodes={pipelineNodes} isProcessing={isProcessing} />

              {/* Loading State Animation */}
              {isProcessing && (
                <ResearchLoadingState
                  query={messages[messages.length - 1]?.content}
                  ticker={selectedTicker}
                />
              )}

              {/* Error Message */}
              {error && (
                <div className="p-4 rounded-xl bg-financial-loss-bg border border-financial-loss/30 text-xs text-financial-loss flex items-start gap-2.5">
                  <ShieldAlert className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <p>{error}</p>
                </div>
              )}

              {/* Research Results Stream */}
              {messages
                .filter((m) => m.role === "assistant")
                .map((msg) => (
                  <ResearchResult
                    key={msg.id}
                    message={msg}
                    onOpenReportMode={() => setIsReportMode(true)}
                    onSelectCitation={(cite) => {
                      setSelectedCitation(cite);
                      setMobileTab("evidence");
                    }}
                  />
                ))}
            </div>

            {/* Right Column: Context Checklist & RAG Evidence Panel (3 Cols on Desktop) */}
            <div
              className={`lg:col-span-3 space-y-6 ${
                mobileTab !== "evidence" ? "hidden lg:block" : "block"
              }`}
            >
              {/* Research Context Transparent Checklist */}
              <ResearchContextPanel contextFlags={contextFlags} />

              {/* RAG Evidence Inspector */}
              <ResearchEvidencePanel
                citations={citations}
                selectedCitation={selectedCitation}
                onSelectCitation={setSelectedCitation}
              />
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
