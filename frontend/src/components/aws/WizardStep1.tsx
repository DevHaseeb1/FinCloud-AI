"use client";

import * as React from "react";
import { Copy, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface WizardStep1Props {
  externalId: string;
  roleName: string;
  loading: boolean;
  onNext: () => void;
}

export function WizardStep1({ externalId, roleName, loading, onNext }: WizardStep1Props) {
  const [copiedField, setCopiedField] = React.useState<string | null>(null);

  const handleCopy = async (label: string, value: string) => {
    await navigator.clipboard.writeText(value);
    setCopiedField(label);
    setTimeout(() => setCopiedField(null), 1500);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <Loader2 className="size-6 text-cyan animate-spin" />
        <p className="text-sm text-muted-foreground">Generating your credentials&hellip;</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <p className="text-sm text-muted-foreground">
        We&apos;ll generate a unique External ID for your connection
      </p>

      <div className="bg-surface-raised rounded-lg p-3 border border-white/8 space-y-1">
        <label className="text-xs text-muted-foreground">External ID</label>
        <div className="flex items-center justify-between">
          <span className="font-mono text-cyan text-sm">{externalId}</span>
          <button
            onClick={() => handleCopy("externalId", externalId)}
            className="size-7 flex items-center justify-center rounded-md hover:bg-white/5 transition-colors duration-100"
            aria-label="Copy External ID"
          >
            {copiedField === "externalId" ? (
              <Check className="size-4 text-emerald-400" style={{ transform: "scale(1.2)", transition: "transform 150ms var(--ease-spring)" }} />
            ) : (
              <Copy className="size-4 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      <div className="bg-surface-raised rounded-lg p-3 border border-white/8 space-y-1">
        <label className="text-xs text-muted-foreground">Role Name</label>
        <div className="flex items-center justify-between">
          <span className="font-mono text-cyan text-sm">{roleName}</span>
          <button
            onClick={() => handleCopy("roleName", roleName)}
            className="size-7 flex items-center justify-center rounded-md hover:bg-white/5 transition-colors duration-100"
            aria-label="Copy Role Name"
          >
            {copiedField === "roleName" ? (
              <Check className="size-4 text-emerald-400" style={{ transform: "scale(1.2)", transition: "transform 150ms var(--ease-spring)" }} />
            ) : (
              <Copy className="size-4 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      <button
        onClick={onNext}
        className="w-full h-9 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
      >
        Next &mdash; Deploy IAM Role &rarr;
      </button>
    </div>
  );
}
