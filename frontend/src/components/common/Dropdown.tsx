"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

export interface DropdownItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: "default" | "danger";
  disabled?: boolean;
}

export interface DropdownProps {
  trigger: React.ReactNode;
  items: (DropdownItem | "divider")[];
  align?: "left" | "right";
  className?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  trigger,
  items,
  align = "right",
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: any) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div ref={menuRef} className="relative inline-block text-left">
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>

      {isOpen && (
        <div
          className={cn(
            "absolute z-50 mt-1.5 w-48 rounded-xl bg-surface border border-border p-1.5 shadow-dropdown animate-in fade-in zoom-in-95 duration-100",
            align === "right" ? "right-0" : "left-0",
            className
          )}
        >
          {items.map((item, index) => {
            if (item === "divider") {
              return <div key={`div-${index}`} className="my-1 border-t border-border-subtle" />;
            }

            return (
              <button
                key={item.id}
                disabled={item.disabled}
                onClick={() => {
                  item.onClick();
                  setIsOpen(false);
                }}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg text-left transition-colors",
                  item.variant === "danger"
                    ? "text-financial-loss hover:bg-financial-loss-bg/50"
                    : "text-content hover:bg-surface-subtle",
                  item.disabled && "opacity-50 cursor-not-allowed"
                )}
              >
                {item.icon && <span className="w-4 h-4 shrink-0">{item.icon}</span>}
                <span className="flex-1">{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
