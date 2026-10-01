'use client';

import React, { useState } from 'react';
import {
  CopilotMode,
  PortfolioCopilotRequest,
  PortfolioCopilotResponse,
  DailyPortfolioBrief,
  UserResearchMemory,
  PortfolioAlert,
  AlertRule,
  AlertEvent,
  PortfolioUserContext,
  DataProvenanceStatus,
  ProvenanceItem,
} from '@/types/portfolio-copilot';
import { PortfolioContextCard } from './PortfolioContextCard';
import { PortfolioRiskSummary } from './PortfolioRiskSummary';
import { PortfolioNewsSummary } from './PortfolioNewsSummary';
import { PortfolioAnomalySummary } from './PortfolioAnomalySummary';
import { PortfolioChangeTimeline } from './PortfolioChangeTimeline';
import { ResearchMemoryPanel } from './ResearchMemoryPanel';
import { PortfolioScenarioPanel } from './PortfolioScenarioPanel';
import { WatchlistIntelligence } from './WatchlistIntelligence';
import { PortfolioAlerts } from './PortfolioAlerts';
import { DailyBriefCard } from './DailyBriefCard';

interface PortfolioCopilotPanelProps {
  userContext?: PortfolioUserContext | null;
  dailyBrief?: DailyPortfolioBrief | null;
  researchMemories?: UserResearchMemory[];
  alerts?: PortfolioAlert[];
  alertRules?: AlertRule[];
  alertEvents?: AlertEvent[];
  onExecuteQuery?: (req: PortfolioCopilotRequest) => Promise<PortfolioCopilotResponse | void>;
  onStreamQuery?: (req: PortfolioCopilotRequest) => void;
  onRefreshBrief?: () => void;
  onCreateAlertRule?: (rule: Partial<AlertRule>) => Promise<void>;
  onDeleteAlertRule?: (ruleId: string) => Promise<void>;
  onAcknowledgeAlert?: (alertId: string) => Promise<void>;
  onRecallMemory?: (memoryId: string) => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  streamingMessage?: string;
  response?: PortfolioCopilotResponse | null;
  className?: string;
}

export const PortfolioCopilotPanel: React.FC<PortfolioCopilotPanelProps> = ({
  userContext,
  dailyBrief,
  researchMemories = [],
  alerts = [],
  alertRules = [],
  alertEvents = [],
  onExecuteQuery,
  onStreamQuery,
  onRefreshBrief,
  onCreateAlertRule,
  onDeleteAlertRule,
  onAcknowledgeAlert,
  onRecallMemory,
  isLoading = false,
  isStreaming = false,
  streamingMessage = '',
  response = null,
  className = '',
}) => {
  const [query, setQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState<CopilotMode>('PORTFOLIO_OVERVIEW');
  const [selectedDepth, setSelectedDepth] = useState<'FAST' | 'STANDARD' | 'DEEP'>('STANDARD');
  const [activeWorkstationTab, setActiveWorkstationTab] = useState<
    'query' | 'brief' | 'context' | 'risk' | 'scenarios' | 'news' | 'anomalies' | 'watchlist' | 'memory' | 'alerts'
  >('query');

  const presetQueries: { label: string; mode: CopilotMode; query: string }[] = [
    {
      label: 'Portfolio Concentration & Exposure',
      mode: 'PORTFOLIO_OVERVIEW',
      query: 'Evaluate my current portfolio concentration, Herfindahl index, and sector risk distribution.',
    },
    {
      label: 'Multi-Pillar Holding Risk & VaR',
      mode: 'RISK_REVIEW',
      query: 'Synthesize parametric 95% VaR, weighted beta, and historical stress scenarios for my holdings.',
    },
    {
      label: 'Changes Since Previous Research',
      mode: 'CHANGE_ANALYSIS',
      query: 'Compare current verified portfolio metrics and holding telemetry against my previous research.',
    },
    {
      label: 'Watchlist Intelligence & Catalysts',
      mode: 'WATCHLIST_RESEARCH',
      query: 'Review factual price dynamics, news events, and anomaly status across my active watchlist.',
    },
    {
      label: 'Portfolio Event & News Review',
      mode: 'NEWS_REVIEW',
      query: 'Aggregate verified regulatory, corporate, and sector news events affecting my active holdings.',
    },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading || isStreaming) return;

    const payload: PortfolioCopilotRequest = {
      query: query.trim(),
      mode: selectedMode,
      depth: selectedDepth,
      symbols: userContext?.holdings.map((h) => h.symbol || h.ticker),
    };

    if (onExecuteQuery) {
      onExecuteQuery(payload);
    }
  };

  const handleApplyPreset = (preset: { mode: CopilotMode; query: string }) => {
    setQuery(preset.query);
    setSelectedMode(preset.mode);
  };

  const getProvenanceBadge = (status?: DataProvenanceStatus) => {
    switch (status) {
      case 'LIVE':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">LIVE</span>;
      case 'CALCULATED':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">CALCULATED</span>;
      case 'MODEL_DERIVED':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded">MODEL-DERIVED</span>;
      case 'HISTORICAL_SCENARIO':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded">HISTORICAL</span>;
      case 'DEMO':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">DEMO</span>;
      case 'STALE':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded">STALE</span>;
      default:
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">{status || 'FACTUAL'}</span>;
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Top Workstation Bar */}
      <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-xl backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-emerald-900/30">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">MarketMind AI Portfolio Copilot</h2>
              <p className="text-xs text-slate-400">
                Personalized research memory, portfolio risk intelligence, deterministic concentration, and multi-agent synthesis.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400 font-medium">Neutrality Policy:</span>
            <span className="px-2 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
              NON-SOLICITATION / FACTUAL
            </span>
          </div>
        </div>

        {/* Query Input Box */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask the portfolio copilot (e.g. 'Analyze concentration risk and changes since last week')..."
              className="w-full px-4 py-3 bg-slate-950/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all pr-28 shadow-inner"
              disabled={isLoading || isStreaming}
            />
            <button
              type="submit"
              disabled={!query.trim() || isLoading || isStreaming}
              className="absolute right-2 top-2 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white disabled:text-slate-500 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 shadow"
            >
              {isLoading || isStreaming ? (
                <>
                  <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Synthesizing...</span>
                </>
              ) : (
                <>
                  <span>Run Copilot</span>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </div>

          {/* Controls Bar: Mode & Depth Selectors */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-slate-400 font-medium">Copilot Mode:</span>
              <select
                value={selectedMode}
                onChange={(e) => setSelectedMode(e.target.value as CopilotMode)}
                className="px-2.5 py-1 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-emerald-500"
              >
                <option value="PORTFOLIO_OVERVIEW">PORTFOLIO_OVERVIEW</option>
                <option value="HOLDING_RESEARCH">HOLDING_RESEARCH</option>
                <option value="WATCHLIST_RESEARCH">WATCHLIST_RESEARCH</option>
                <option value="CHANGE_ANALYSIS">CHANGE_ANALYSIS</option>
                <option value="RISK_REVIEW">RISK_REVIEW</option>
                <option value="NEWS_REVIEW">NEWS_REVIEW</option>
                <option value="SCENARIO_REVIEW">SCENARIO_REVIEW</option>
                <option value="WEEKLY_REVIEW">WEEKLY_REVIEW</option>
                <option value="DAILY_BRIEF">DAILY_BRIEF</option>
              </select>

              <span className="text-slate-400 font-medium ml-2">Depth:</span>
              <div className="inline-flex rounded-lg border border-slate-700 bg-slate-800 p-0.5">
                {(['FAST', 'STANDARD', 'DEEP'] as const).map((d) => (
                  <button
                    type="button"
                    key={d}
                    onClick={() => setSelectedDepth(d)}
                    className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                      selectedDepth === d ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-slate-500 text-[11px]">Quick Queries:</span>
              {presetQueries.slice(0, 3).map((p, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => handleApplyPreset(p)}
                  className="px-2 py-0.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 rounded text-[11px] text-slate-300 transition-colors"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </form>

        {/* Streaming / Loading Feedback */}
        {(isStreaming || isLoading) && (
          <div className="mt-4 p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></div>
              <span className="text-xs text-emerald-300 font-mono">
                {streamingMessage || 'Multi-agent orchestration active: evaluating holdings, risk scenarios, and memory...'}
              </span>
            </div>
            <span className="text-[10px] text-emerald-400/80 font-mono uppercase tracking-wider">SSE Stream</span>
          </div>
        )}
      </div>

      {/* Main Navigation Subtabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {[
          { key: 'query', label: 'AI Copilot Synthesis' },
          { key: 'brief', label: 'Daily Brief' },
          { key: 'context', label: 'Portfolio Context' },
          { key: 'risk', label: 'Risk & Concentration' },
          { key: 'scenarios', label: 'Stress & Scenarios' },
          { key: 'news', label: 'Holding News' },
          { key: 'anomalies', label: 'Anomalies' },
          { key: 'watchlist', label: 'Watchlist' },
          { key: 'memory', label: `Research Memory (${researchMemories.length})` },
          { key: 'alerts', label: `Factual Alerts (${alerts.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveWorkstationTab(tab.key as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeWorkstationTab === tab.key
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/30 shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Subtab 1: AI Copilot Synthesis */}
      {activeWorkstationTab === 'query' && (
        <div className="space-y-6">
          {response ? (
            <div className="space-y-6">
              {/* Report Header */}
              <div className="p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-xl space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </span>
                    <div>
                      <h3 className="text-base font-bold text-slate-100">{response.report.title}</h3>
                      <p className="text-xs text-slate-400">
                        Query: &quot;{response.query}&quot; • Mode: <span className="text-emerald-400 font-mono">{response.mode}</span>
                      </p>
                    </div>
                  </div>

                  {response.confidence && (
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Confidence</span>
                        <span className="text-xs font-bold text-emerald-400 font-mono">
                          {((response.confidence.confidence_score ?? 0.85) * 100).toFixed(0)}% ({response.confidence.confidence_level})
                        </span>
                      </div>
                      {getProvenanceBadge((response.provenance as any)?.overall_status || 'LIVE')}
                    </div>
                  )}
                </div>

                {/* Executive Summary */}
                {response.report.executive_summary && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Executive Synthesis</h4>
                    <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs text-slate-200 leading-relaxed space-y-2 whitespace-pre-line font-sans">
                      {response.report.executive_summary}
                    </div>
                  </div>
                )}

                {/* Evidence & Pillars Grid */}
                {response.evidence && response.evidence.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Pillar Evidence & Verified Telemetry</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {response.evidence.map((ev: any, idx: number) => (
                        <div key={idx} className="p-3 bg-slate-950/50 border border-slate-800 rounded-lg space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-200 font-mono">{ev.source_agent || ev.source_name}</span>
                            <span className="text-[10px] text-slate-400 font-mono">{ev.retrieved_at || ev.timestamp}</span>
                          </div>
                          <p className="text-xs text-slate-300">{ev.claim || ev.content || ev.title}</p>
                          <div className="flex items-center gap-2 pt-1 text-[10px] text-slate-500">
                            {ev.confidence && <span>Confidence: {(ev.confidence * 100).toFixed(0)}%</span>}
                            {ev.pillar && (
                              <>
                                <span>•</span>
                                <span>Pillar: {ev.pillar}</span>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Structured Sections */}
                {response.report.sections && response.report.sections.map((sec: any, idx: number) => (
                  <div key={idx} className="p-4 bg-slate-950/40 border border-slate-800/70 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">{sec.heading || sec.title}</h4>
                      {sec.provenance_status && getProvenanceBadge(sec.provenance_status)}
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">{sec.content}</p>
                    {sec.bullet_points && sec.bullet_points.length > 0 && (
                      <ul className="list-disc list-inside space-y-1 text-xs text-slate-400 pl-1">
                        {sec.bullet_points.map((pt: string, pIdx: number) => (
                          <li key={pIdx}>{pt}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}

                {/* Citations & Disclaimers */}
                <div className="pt-4 border-t border-slate-800/80 space-y-3">
                  {response.citations && response.citations.length > 0 && (
                    <div>
                      <h5 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Cited Sources</h5>
                      <div className="flex flex-wrap gap-2">
                        {response.citations.map((c, idx) => (
                          <span key={idx} className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded text-[11px] text-slate-300 font-mono">
                            [{c.source_id || c.citation_id}] {c.title || c.source_name} ({c.source_type})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {response.limitations && response.limitations.length > 0 && (
                    <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-[10px] text-slate-400 space-y-1">
                      <span className="font-semibold text-slate-300 uppercase tracking-wider block">Institutional Limitations:</span>
                      <p>{response.limitations.join(' • ')}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Integrated Change Timeline if changes present */}
              {response.changes && (
                <PortfolioChangeTimeline changeReport={response.changes} />
              )}
            </div>
          ) : (
            <div className="p-12 bg-slate-900/90 border border-slate-800 rounded-xl text-center space-y-4 shadow-xl">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shadow-inner">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-200">Portfolio Copilot Ready</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                  Ask questions about your holdings, concentration, risk factors, or historical research changes.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Subtab 2: Daily Brief */}
      {activeWorkstationTab === 'brief' && (
        <DailyBriefCard brief={dailyBrief} onRefresh={onRefreshBrief} isLoading={isLoading} />
      )}

      {/* Subtab 3: Portfolio Context */}
      {activeWorkstationTab === 'context' && userContext && (
        <PortfolioContextCard context={userContext} />
      )}

      {/* Subtab 4: Risk & Concentration */}
      {activeWorkstationTab === 'risk' && userContext?.risk_context && (
        <PortfolioRiskSummary risk={userContext.risk_context} />
      )}

      {/* Subtab 5: Scenarios & Stress */}
      {activeWorkstationTab === 'scenarios' && userContext?.risk_context && (
        <PortfolioScenarioPanel risk={userContext.risk_context} />
      )}

      {/* Subtab 6: News Intelligence */}
      {activeWorkstationTab === 'news' && userContext?.news_context && (
        <PortfolioNewsSummary news={userContext.news_context} />
      )}

      {/* Subtab 7: Anomalies */}
      {activeWorkstationTab === 'anomalies' && userContext?.anomaly_context && (
        <PortfolioAnomalySummary anomaly={userContext.anomaly_context} />
      )}

      {/* Subtab 8: Watchlist */}
      {activeWorkstationTab === 'watchlist' && userContext?.watchlist && (
        <WatchlistIntelligence watchlist={userContext.watchlist} />
      )}

      {/* Subtab 9: Research Memory */}
      {activeWorkstationTab === 'memory' && (
        <ResearchMemoryPanel
          memories={researchMemories}
          onSelectMemory={onRecallMemory ? (m) => onRecallMemory(m.research_id) : undefined}
        />
      )}

      {/* Subtab 10: Factual Alerts */}
      {activeWorkstationTab === 'alerts' && (
        <PortfolioAlerts
          alerts={alerts}
          rules={alertRules}
          onCreateRule={onCreateAlertRule ? (type, threshold, sym) => onCreateAlertRule({ rule_type: type, threshold, symbol: sym }) : undefined}
          onDeleteRule={onDeleteAlertRule}
          onMarkRead={onAcknowledgeAlert}
        />
      )}
    </div>
  );
};
