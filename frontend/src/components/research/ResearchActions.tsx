"use client";

import React, { useState } from "react";
import { Button } from "@/components/common/Button";
import { Copy, Check, RotateCcw, Bookmark, FileText, Share2, CornerDownLeft } from "lucide-react";

export interface ResearchActionsProps {
  onCopy: () => void;
  onRegenerate?: () => void;
  onSave?: () => void;
  onReportMode?: () => void;
}

export const ResearchActions: React.FC<ResearchActionsProps> = ({
  onCopy,
  onRegenerate,
  onSave,
  onReportMode,
}) => {
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleCopyClick = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveClick = () => {
    onSave?.();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex flex-wrap items-center gap-2 pt-2">
      <Button
        variant="outline"
        size="sm"
        onClick={handleCopyClick}
        leftIcon={copied ? <Check className="w-3.5 h-3.5 text-financial-gain" /> : <Copy className="w-3.5 h-3.5 text-content-muted" />}
      >
        {copied ? "Copied" : "Copy"}
      </Button>

      {onRegenerate && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRegenerate}
          leftIcon={<RotateCcw className="w-3.5 h-3.5 text-content-muted" />}
        >
          Regenerate
        </Button>
      )}

      {onSave && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleSaveClick}
          leftIcon={saved ? <Check className="w-3.5 h-3.5 text-accent" /> : <Bookmark className="w-3.5 h-3.5 text-content-muted" />}
        >
          {saved ? "Saved" : "Save Research"}
        </Button>
      )}

      {onReportMode && (
        <Button
          variant="gold"
          size="sm"
          onClick={onReportMode}
          leftIcon={<FileText className="w-3.5 h-3.5" />}
        >
          Generate Report
        </Button>
      )}
    </div>
  );
};
