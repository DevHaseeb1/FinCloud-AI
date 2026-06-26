"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const sizeMap = {
  sm: { box: 7, icon: 4, text: "text-sm", gap: 2 },
  md: { box: 8, icon: 5, text: "text-lg", gap: 2.5 },
  lg: { box: 10, icon: 6, text: "text-xl", gap: 3 },
} as const;

interface LogoProps {
  showText?: boolean;
  size?: keyof typeof sizeMap;
  subtitle?: string;
  className?: string;
}

export function Logo({ showText = true, size = "md", subtitle, className }: LogoProps) {
  const s = sizeMap[size];

  return (
    <div className={cn("flex items-center", className)} style={{ gap: `${s.gap * 4}px` }}>
      <div
        className={cn("flex shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-cyan to-violet")}
        style={{ width: `${s.box * 4}px`, height: `${s.box * 4}px` }}
      >
        <svg
          width={s.icon * 4}
          height={s.icon * 4}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M5 14.5a4 4 0 0 1 2.5-7 5.5 5.5 0 0 1 10.2-1.7A4.5 4.5 0 0 1 18 14.5H6a1 1 0 0 1-1-1z"
            fill="white"
            opacity="0.9"
          />
          <path
            d="M9 14.5v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3M12 10.5v-3M8 17.5h8M9.5 17.5l-1 3M14.5 17.5l1 3"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity="0.9"
          />
        </svg>
      </div>
      {showText && (
        <div className="flex flex-col leading-tight">
          <span className={cn("font-bold text-white", s.text)}>FinCloud-AI</span>
          {subtitle && <span className="text-xs text-white/50">{subtitle}</span>}
        </div>
      )}
    </div>
  );
}
