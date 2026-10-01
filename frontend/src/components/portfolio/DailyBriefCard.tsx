'use client';

import React, { useState } from 'react';
import {
  DailyPortfolioBrief,
  DataProvenanceStatus,
  ProvenanceItem,
} from '@/types/portfolio-copilot';

interface DailyBriefCardProps {
  brief?: DailyPortfolioBrief | null;
  isLoading?: boolean;
  onRefresh?: () => void;
  className?: string;
}

export const DailyBriefCard: React.FC<DailyBriefCardProps> = ({
  brief,
  isLoading = false,
  onRefresh,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'changes' | 'news' | 'risk' | 'anomalies' | 'watchlist' | 'provenance'>('overview');

  if (isLoading) {
    return (
      <div className={`p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-lg backdrop-blur animate-pulse ${className}`}>
        <div className="flex justify-between items-center mb-6">
          <div className="h-6 w-48 bg-slate-800 rounded"></div>
          <div className="h-5 w-24 bg-slate-800 rounded-full"></div>
        </div>
        <div className="space-y-4">
          <div className="h-20 bg-slate-800/60 rounded-lg"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="h-16 bg-slate-800/60 rounded-lg"></div>
            <div className="h-16 bg-slate-800/60 rounded-lg"></div>
            <div className="h-16 bg-slate-800/60 rounded-lg"></div>
            <div className="h-16 bg-slate-800/60 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!brief) {
    return (
      <div className={`p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-lg text-center ${className}`}>
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/80 flex items-center justify-center text-slate-400">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-slate-200">No Daily Brief Generated Yet</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
          Generate an institutional brief summarizing factual changes, concentration shifts, anomalies, and verified news.
        </p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="mt-4 px-4 py-2 text-xs font-medium bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 rounded-lg hover:bg-emerald-600/30 transition-colors"
          >
            Generate Daily Brief
          </button>
        )}
      </div>
    );
  }

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const getProvenanceBadge = (status: DataProvenanceStatus) => {
    switch (status) {
      case 'LIVE':
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">CURRENT FACT (LIVE)</span>;
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
        return <span className="px-2 py-0.5 text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">{status}</span>;
    }
  };

  return (
    <div className={`p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-xl backdrop-blur ${className}`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </span>
            <h3 className="text-lg font-bold text-slate-100">Daily Portfolio Intelligence Brief</h3>
            <span className="text-xs text-slate-400 font-mono">[{brief.date}]</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Factual synthesis of portfolio metrics, market movers, concentration shifts, anomalies, and verified events.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {getProvenanceBadge(brief.provenance_status)}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
              title="Refresh Brief"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Snapshot Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
          <span className="text-[11px] text-slate-400 font-medium">Total Portfolio Value</span>
          <p className="text-base font-bold text-slate-100 font-mono mt-0.5">
            {formatCurrency(brief.portfolio_value)}
          </p>
        </div>
        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
          <span className="text-[11px] text-slate-400 font-medium">Daily Change</span>
          <p className={`text-base font-bold font-mono mt-0.5 ${brief.daily_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {brief.daily_pnl >= 0 ? '+' : ''}{formatCurrency(brief.daily_pnl)} ({brief.daily_pnl_pct >= 0 ? '+' : ''}{brief.daily_pnl_pct.toFixed(2)}%)
          </p>
        </div>
        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
          <span className="text-[11px] text-slate-400 font-medium">Anomalies / News</span>
          <p className="text-base font-bold text-slate-100 font-mono mt-0.5">
            <span className={brief.anomalies.length > 0 ? 'text-amber-400' : 'text-slate-300'}>
              {brief.anomalies.length}
            </span>
            <span className="text-slate-500 text-xs font-normal"> / </span>
            <span className="text-blue-400">{brief.important_news.length}</span>
          </p>
        </div>
        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
          <span className="text-[11px] text-slate-400 font-medium">Data Quality Flag</span>
          <p className="text-sm font-semibold text-slate-200 mt-1 truncate">
            {brief.data_quality_notes ? (
              <span className="text-amber-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                Review Required
              </span>
            ) : (
              <span className="text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Verified Clean
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-1 p-1 bg-slate-950/80 rounded-lg border border-slate-800 mb-4 text-xs font-medium">
        {[
          { key: 'overview', label: 'Overview & Movers' },
          { key: 'changes', label: `What Changed (${brief.changes_since_previous.length})` },
          { key: 'news', label: `News (${brief.important_news.length})` },
          { key: 'risk', label: 'Risk & Concentration' },
          { key: 'anomalies', label: `Anomalies (${brief.anomalies.length})` },
          { key: 'watchlist', label: `Watchlist (${brief.watchlist_developments.length})` },
          { key: 'provenance', label: 'Provenance & Audit' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === tab.key
                ? 'bg-emerald-600 text-white font-semibold shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div className="p-4 bg-slate-950/40 border border-slate-800/60 rounded-lg">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Executive Overview</h4>
            <p className="text-xs text-slate-300 leading-relaxed">{brief.summary}</p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Largest Factual Movers</h4>
            {brief.largest_movers.length === 0 ? (
              <p className="text-xs text-slate-500 italic p-3 bg-slate-950/40 rounded-lg border border-slate-800/50">No significant holding movers recorded today.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {brief.largest_movers.map((mover, idx) => (
                  <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-slate-200 font-mono">{mover.symbol}</span>
                      <p className="text-[11px] text-slate-400 font-mono">₹{mover.current_price.toFixed(2)}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs font-bold font-mono ${mover.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {mover.change_pct >= 0 ? '+' : ''}{mover.change_pct.toFixed(2)}%
                      </span>
                      <p className="text-[10px] text-slate-500">Weight: {(mover.portfolio_weight * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'changes' && (
        <div className="space-y-2">
          {brief.changes_since_previous.length === 0 ? (
            <p className="text-xs text-slate-500 italic p-4 bg-slate-950/40 rounded-lg border border-slate-800/50">No structural changes detected since previous brief.</p>
          ) : (
            brief.changes_since_previous.map((chg, idx) => (
              <div key={idx} className="p-3 bg-slate-950/50 border border-slate-800/80 rounded-lg flex items-start gap-3">
                <span className="p-1 rounded bg-blue-500/10 text-blue-400 text-xs font-mono font-bold">{chg.symbol || 'PORTFOLIO'}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-300">{chg.metric}</span>
                    <span className="text-[10px] text-slate-500 font-mono">{chg.direction}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{chg.description}</p>
                  <div className="flex items-center gap-4 text-[10px] text-slate-500 font-mono mt-2">
                    <span>Prior: {String(chg.prior_value ?? 'N/A')}</span>
                    <span>→</span>
                    <span className="text-slate-300 font-medium">Current: {String(chg.current_value ?? 'N/A')}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'news' && (
        <div className="space-y-2">
          {brief.important_news.length === 0 ? (
            <p className="text-xs text-slate-500 italic p-4 bg-slate-950/40 rounded-lg border border-slate-800/50">No high-impact news items recorded in this interval.</p>
          ) : (
            brief.important_news.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-slate-200">{item.headline}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{item.timestamp}</span>
                </div>
                <div className="flex flex-wrap items-center gap-2 mt-2 text-[10px]">
                  <span className="text-slate-400">Source: <strong className="text-slate-300">{item.source}</strong></span>
                  {item.symbols && (
                    <div className="flex gap-1">
                      {item.symbols.map((sym, sIdx) => (
                        <span key={sIdx} className="px-1.5 py-0.2 bg-slate-800 text-slate-300 rounded font-mono">{sym}</span>
                      ))}
                    </div>
                  )}
                  <span className="px-1.5 py-0.2 bg-slate-800/80 text-slate-400 rounded">{item.event_category}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'risk' && (
        <div className="space-y-3">
          <div className="p-3 bg-slate-950/50 border border-slate-800 rounded-lg">
            <h4 className="text-xs font-semibold text-slate-300 mb-1">Concentration Dynamics</h4>
            <p className="text-xs text-slate-400">{brief.concentration_changes || 'Concentration profile is stable within normal limits.'}</p>
          </div>
          <div className="p-3 bg-slate-950/50 border border-slate-800 rounded-lg">
            <h4 className="text-xs font-semibold text-slate-300 mb-1">Risk Metric Variations</h4>
            <p className="text-xs text-slate-400">{brief.risk_changes || 'No elevated parametric tail-risk or volatility spikes recorded.'}</p>
          </div>
        </div>
      )}

      {activeTab === 'anomalies' && (
        <div className="space-y-2">
          {brief.anomalies.length === 0 ? (
            <p className="text-xs text-slate-500 italic p-4 bg-slate-950/40 rounded-lg border border-slate-800/50">No volume or volatility anomalies detected for current holdings.</p>
          ) : (
            brief.anomalies.map((anom, idx) => (
              <div key={idx} className="p-3 bg-amber-950/10 border border-amber-500/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-300 font-mono">{anom.symbol}</span>
                  <span className="text-[10px] text-amber-400/80 uppercase font-mono">{anom.anomaly_type}</span>
                </div>
                <p className="text-xs text-slate-300 mt-1">{anom.description}</p>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400">
                  <span>Z-Score: <strong className="font-mono text-slate-200">{anom.z_score.toFixed(2)}</strong></span>
                  <span>Co-occurrence: <strong className="text-slate-300">{anom.associative_factors.join(', ') || 'Isolated'}</strong></span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'watchlist' && (
        <div className="space-y-2">
          {brief.watchlist_developments.length === 0 ? (
            <p className="text-xs text-slate-500 italic p-4 bg-slate-950/40 rounded-lg border border-slate-800/50">No major developments recorded across your active watchlist.</p>
          ) : (
            brief.watchlist_developments.map((dev, idx) => (
              <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-start gap-3">
                <span className="p-1 rounded bg-slate-800 text-slate-200 text-xs font-mono font-bold">{dev.symbol}</span>
                <div className="flex-1">
                  <span className="text-xs font-semibold text-slate-300">{dev.development_type}</span>
                  <p className="text-xs text-slate-400 mt-0.5">{dev.description}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'provenance' && (
        <div className="space-y-3">
          <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
            <span className="text-xs font-semibold text-slate-300">Data Integrity & Quality Notes</span>
            <p className="text-xs text-slate-400 mt-1">{brief.data_quality_notes || 'All upstream feeds passed verification without telemetry gaps.'}</p>
          </div>
          <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
            <span className="text-xs font-semibold text-slate-300">Origin Traceability</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {brief.provenance.map((prov: ProvenanceItem, idx: number) => (
                <span key={idx} className="px-2 py-1 bg-slate-800/80 border border-slate-700/60 rounded text-[10px] text-slate-300 font-mono">
                  {prov.source_name} ({prov.status})
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Neutrality Disclaimer */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 flex items-center justify-between">
        <span>Factual intelligence synthesis. Not financial advice or directional solicitation.</span>
        <span>MarketMind AI Copilot</span>
      </div>
    </div>
  );
};
