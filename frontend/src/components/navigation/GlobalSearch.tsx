"use client";

import React, { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/common/Modal";
import { useGlobalSearch } from "@/hooks/useGlobalSearch";
import {
  SearchInput,
  SearchCategoryTabs,
  SearchResultItem,
  RecentSearches,
  SearchEmptyState,
  SearchKeyboardHints,
} from "@/components/search";
import { Brain, ArrowRight } from "lucide-react";
import { GlobalSearchResultItem } from "@/types";

export interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

function getItemTerm(item: GlobalSearchResultItem): string {
  if ("ticker" in item && typeof item.ticker === "string") return item.ticker;
  if ("label" in item && typeof item.label === "string") return item.label;
  if ("title" in item && typeof item.title === "string") return item.title;
  if ("query" in item && typeof item.query === "string") return item.query;
  return "";
}

function getItemKey(item: GlobalSearchResultItem): string {
  if ("id" in item && typeof item.id === "string") return item.id;
  if ("ticker" in item && typeof item.ticker === "string") return item.ticker;
  if ("label" in item && typeof item.label === "string") return item.label;
  if ("query" in item && typeof item.query === "string") return item.query;
  return item.type;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({ isOpen, onClose }) => {
  const router = useRouter();
  const listRef = useRef<HTMLDivElement>(null);

  const {
    query,
    setQuery,
    category,
    setCategory,
    results,
    activeIndex,
    setActiveIndex,
    recentSearches,
    addRecentSearch,
    removeRecentSearch,
    clearRecentSearches,
  } = useGlobalSearch();

  // Global Cmd+K / Ctrl+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          window.dispatchEvent(new CustomEvent("marketmind:open-search"));
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Modal-level Keyboard Navigation (ArrowUp, ArrowDown, Enter)
  useEffect(() => {
    if (!isOpen) return;

    const handleModalKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIndex((prev) => (results.length > 0 ? (prev + 1) % results.length : 0));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIndex((prev) => (results.length > 0 ? (prev - 1 + results.length) % results.length : 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (results.length > 0 && results[activeIndex]) {
          const item = results[activeIndex];
          const term = query || getItemTerm(item);
          addRecentSearch(term);
          router.push(item.url);
          onClose();
          setQuery("");
        } else if (query.trim().length > 0) {
          addRecentSearch(query);
          router.push(`/research?q=${encodeURIComponent(query)}`);
          onClose();
          setQuery("");
        }
      }
    };

    window.addEventListener("keydown", handleModalKeyDown);
    return () => window.removeEventListener("keydown", handleModalKeyDown);
  }, [isOpen, results, activeIndex, query, addRecentSearch, router, onClose, setQuery, setActiveIndex]);

  const handleSelectItem = (url: string, term?: string) => {
    if (term) addRecentSearch(term);
    else if (query.trim()) addRecentSearch(query);
    router.push(url);
    onClose();
    setQuery("");
  };

  const handleAskAI = (q: string) => {
    addRecentSearch(q);
    router.push(`/research?q=${encodeURIComponent(q)}`);
    onClose();
    setQuery("");
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="xl" className="p-0 overflow-hidden bg-surface rounded-2xl shadow-2xl border border-border">
      {/* 1. Search Input Bar */}
      <SearchInput
        query={query}
        onChange={setQuery}
        onClear={() => setQuery("")}
      />

      {/* 2. Category Selector Tabs */}
      <SearchCategoryTabs
        activeCategory={category}
        onSelectCategory={setCategory}
      />

      {/* 3. Results / Recent Searches / AI CTA Container */}
      <div ref={listRef} className="max-h-[420px] overflow-y-auto p-4 space-y-3.5 scrollbar-thin">
        {/* Recent Searches chips (when query is empty and category is ALL) */}
        {!query.trim() && category === "ALL" && (
          <RecentSearches
            searches={recentSearches}
            onSelectSearch={(term) => setQuery(term)}
            onRemoveSearch={removeRecentSearch}
            onClearAll={clearRecentSearches}
          />
        )}

        {/* Deep AI Research trigger if user entered a custom text query */}
        {query.trim().length >= 3 && (
          <div
            onClick={() => handleAskAI(query)}
            className="flex items-center justify-between p-3 rounded-xl bg-primary-light/60 border border-primary/20 hover:bg-primary-light cursor-pointer transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-primary text-white shrink-0">
                <Brain className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-primary">Run Deep AI Research</p>
                <p className="text-[11px] text-content-muted">
                  Analyze &ldquo;{query}&rdquo; via LangGraph multi-agent + SEC 10-K RAG
                </p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-primary shrink-0" />
          </div>
        )}

        {/* Results List */}
        {results.length > 0 ? (
          <div className="space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-wider text-content-muted px-1 mb-1.5">
              {query.trim() ? `Search Results (${results.length})` : "Featured Commands & Markets"}
            </p>
            {results.map((item, idx) => (
              <SearchResultItem
                key={`${item.type}-${getItemKey(item)}-${idx}`}
                item={item}
                isActive={idx === activeIndex}
                onSelect={() => handleSelectItem(item.url, getItemTerm(item))}
              />
            ))}
          </div>
        ) : (
          query.trim() && (
            <SearchEmptyState
              query={query}
              onAskAI={handleAskAI}
            />
          )
        )}
      </div>

      {/* 4. Keyboard Shortcuts Footer */}
      <SearchKeyboardHints />
    </Modal>
  );
};
