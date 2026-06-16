"use client";

import * as React from "react";
import { Check, ChevronLeft, X } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { ValidationChecklist } from "@/components/aws/ValidationChecklist";
import type { AwsTestCheck } from "@/types/apiTypes";

interface WizardStep4Props {
  checks: AwsTestCheck[];
  loading: boolean;
  overallStatus: string | null;
  connectionId: number | null;
  onGoBack: () => void;
  onRetry: () => void;
  onSkipCur: () => void;
  onEdit: () => void;
}

export function WizardStep4({
  checks,
  loading,
  overallStatus,
  connectionId,
  onGoBack,
  onRetry,
  onSkipCur,
  onEdit,
}: WizardStep4Props) {
  const [shake, setShake] = React.useState(false);

  React.useEffect(() => {
    if (overallStatus === "error") {
      setShake(true);
      setTimeout(() => setShake(false), 400);
    }
  }, [overallStatus]);

  if (loading) {
    return (
      <div className="space-y-4 py-4">
        <p className="text-sm text-muted-foreground text-center">Validating your connection&hellip;</p>
        <ValidationChecklist checks={checks} animating />
      </div>
    );
  }

  if (overallStatus === "success") {
    return (
      <div className="space-y-5 py-2" style={{ animation: "fade-up 300ms var(--ease-out-expo)" }}>
        <div className="flex items-center gap-3">
          <span className="size-8 flex items-center justify-center rounded-full bg-emerald-500/15">
            <Check className="size-5 text-emerald-400" style={{ animation: "scaleIn 300ms var(--ease-spring)" }} />
          </span>
          <div>
            <p className="text-sm font-semibold text-foreground">Connection verified</p>
          </div>
        </div>

        <div className="space-y-2 pl-11">
          {checks.map((c, i) => (
            <div key={i} className="flex items-center gap-2 text-xs" style={{ animation: `fade-up 200ms ${i * 100}ms var(--ease-out-expo) both` }}>
              <Check className="size-3 text-emerald-400" />
              <span className="text-muted-foreground">{c.message || c.check}</span>
            </div>
          ))}
        </div>

        <div className="space-y-2 pt-2">
          <Link
            href="/aws"
            className="flex items-center justify-center w-full h-9 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
          >
            Go to Dashboard
          </Link>
          <Link
            href={`/aws/${connectionId}`}
            className="flex items-center justify-center w-full text-xs text-muted-foreground hover:text-cyan transition-colors duration-100"
          >
            View connection
          </Link>
        </div>
      </div>
    );
  }

  if (overallStatus === "partial") {
    return (
      <div className="space-y-5 py-2">
        <ValidationChecklist checks={checks} />

        <div className="bg-surface-raised rounded-lg p-3 border border-white/8">
          {checks.filter((c) => c.status === "error").map((c, i) => (
            <p key={i} className="text-xs text-muted-foreground">
              {c.check === "CUR bucket access" ? "Check that the S3 bucket name is correct" : c.message}
            </p>
          ))}
        </div>

        <div className="flex gap-2">
          <button
            onClick={onEdit}
            className="flex-1 h-8 rounded-lg border border-white/8 text-sm text-muted-foreground hover:bg-white/5 transition-colors duration-100"
          >
            Edit connection
          </button>
          <button
            onClick={onSkipCur}
            className="flex-1 h-8 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
          >
            Skip CUR &mdash; use Cost Explorer only
          </button>
        </div>
      </div>
    );
  }

  if (overallStatus === "error") {
    return (
      <div
        className={cn("space-y-5 py-2", shake && "animate-shake")}
        style={{ animation: shake ? "shake 400ms" : undefined }}
      >
        <div className="flex items-center gap-3">
          <span className="size-8 flex items-center justify-center rounded-full bg-ember/15">
            <X className="size-5 text-ember" />
          </span>
          <div>
            <p className="text-sm font-semibold text-foreground">Could not connect to AWS</p>
          </div>
        </div>

        <ValidationChecklist checks={checks} />

        {checks.find((c) => c.check === "STS AssumeRole" && c.status === "error") && (
          <p className="text-xs text-muted-foreground bg-surface-raised rounded-lg p-3 border border-white/8">
            This usually means the Role ARN is incorrect or the CloudFormation stack hasn&apos;t finished deploying.
          </p>
        )}

        <div className="flex gap-2">
          <button
            onClick={onGoBack}
            className="flex-1 h-8 rounded-lg border border-white/8 text-sm text-muted-foreground hover:bg-white/5 transition-colors duration-100"
          >
            <span className="flex items-center justify-center gap-1">
              <ChevronLeft className="size-4" /> Go back
            </span>
          </button>
          <button
            onClick={onRetry}
            className="flex-1 h-8 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
          >
            Retry validation
          </button>
        </div>
      </div>
    );
  }

  return null;
}
