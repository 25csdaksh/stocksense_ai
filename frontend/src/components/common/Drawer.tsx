"use client";

import React, { useEffect } from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  position?: "left" | "right";
  children: React.ReactNode;
  width?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  position = "right",
  children,
  width = "md",
  className,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widths = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div
        className="absolute inset-0 bg-primary-dark/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div
        className={cn(
          "fixed inset-y-0 flex max-w-full",
          position === "right" ? "right-0 pl-10" : "left-0 pr-10"
        )}
      >
        <div
          className={cn(
            "w-screen bg-surface border-l border-border shadow-modal flex flex-col",
            widths[width],
            position === "left" && "border-r border-l-0",
            className
          )}
        >
          <div className="flex items-center justify-between p-5 border-b border-border">
            {title && <h3 className="text-base font-bold text-content">{title}</h3>}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-content-muted hover:text-content hover:bg-surface-subtle transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="p-5 flex-1 overflow-y-auto">{children}</div>
        </div>
      </div>
    </div>
  );
};
