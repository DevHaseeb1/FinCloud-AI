"use client";

import * as React from "react";
import { Check, X, Loader2, Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import type { AwsTestCheck } from "@/types/apiTypes";

interface ValidationChecklistProps {
  checks: AwsTestCheck[];
  animating?: boolean;
}

export function ValidationChecklist({ checks, animating }: ValidationChecklistProps) {
  const reduced = useReducedMotion();
  const [visible, setVisible] = React.useState<number[]>([]);

  React.useEffect(() => {
    if (!animating) {
      setVisible(checks.map((_, i) => i));
      return;
    }
    checks.forEach((_, i) => {
      const delay = reduced ? 0 : i * 400;
      setTimeout(() => setVisible((prev) => [...prev, i]), delay);
    });
  }, [checks, animating, reduced]);

  return (
    <div className="space-y-3">
      {checks.map((check, i) => {
        const isVisible = visible.includes(i);
        const isSuccess = check.status === "success";
        const isError = check.status === "error";
        const isWarning = check.status === "warning";
        const isSkipped = check.status === "skipped";

        return (
          <div
            key={i}
            className={cn(
              "flex items-center gap-3 transition-all duration-200",
              !isVisible && "opacity-0 scale-0",
              isVisible && "opacity-100 scale-100",
            )}
            style={{
              transitionTimingFunction: "var(--ease-spring)",
              transformOrigin: "left center",
            }}
          >
            <span className="size-5 flex items-center justify-center shrink-0">
              {isSuccess ? (
                <Check className="size-4 text-emerald-400" style={{ animation: "scaleIn 300ms var(--ease-spring)" }} />
              ) : isError ? (
                <X className="size-4 text-ember" style={{ animation: "scaleIn 300ms var(--ease-spring)" }} />
              ) : isWarning ? (
                <Circle className="size-4 text-amber-400" />
              ) : isVisible ? (
                <Circle className="size-4 text-muted-foreground/40" />
              ) : (
                <Loader2 className="size-4 text-cyan animate-spin" />
              )}
            </span>
            <div className="flex-1 min-w-0">
              <span className="font-mono text-sm">{check.check}</span>
              {check.message && (
                <p className="text-xs text-muted-foreground mt-0.5 truncate">{check.message}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
