"use client";

import * as React from "react";
import {
  TriangleAlert,
  AlertCircle,
  AlertTriangle,
  X,
  ChevronDown,
  ChevronUp,
  Filter,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAnomalies } from "@/hooks/useAnomalies";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { formatCurrency } from "@/lib/format";
import { staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";
import type { Anomaly, AnomalyExplanation } from "@/types/apiTypes";
import type { AnomalyFilterParams } from "@/services/anomalyService";

// ── Helpers ─────────────────────────────────────────────────────────────────

function scoreColor(score: number | undefined): string {
  if (score == null) return "bg-muted text-muted-foreground";
  if (score >= 0.8) return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
  if (score >= 0.6) return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
  return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
}

function severityIcon(sev?: string) {
  if (sev === "high") return <AlertTriangle className="size-4 text-red-500/70" />;
  if (sev === "medium") return <AlertCircle className="size-4 text-amber-500/70" />;
  return <TriangleAlert className="size-4 text-blue-500/70" />;
}

function severityVariant(sev?: string) {
  if (sev === "high") return "destructive" as const;
  if (sev === "medium") return "secondary" as const;
  return "outline" as const;
}

function truncate(s: string, max = 80): string {
  if (s.length <= max) return s;
  return s.slice(0, max).trimEnd() + "…";
}

// ── Filter chip definitions ─────────────────────────────────────────────────

interface FilterChip {
  label: string;
  param: keyof AnomalyFilterParams;
  value: number | boolean;
}

const FILTER_CHIPS: FilterChip[] = [
  { label: "Cost spike (zscore > 3)", param: "cost_zscore_gt", value: 3 },
  { label: "Above P95 (> 2×)", param: "cost_ratio_p95_gt", value: 2 },
  { label: "Efficiency anomaly (> 5×)", param: "cost_per_unit_ratio_gt", value: 5 },
  { label: "Has errors", param: "has_errors", value: true },
];

// ── Signal bar chart thresholds ─────────────────────────────────────────────

function signalThreshold(key: string): number {
  switch (key) {
    case "cost_zscore":
      return 3;
    case "cost_ratio_p95":
      return 2;
    case "daily_spend_zscore":
      return 3;
    case "cost_per_unit_ratio":
      return 5;
    case "error_count":
      return 0;
    default:
      return Infinity;
  }
}

function signalLabel(key: string): string {
  switch (key) {
    case "cost_zscore":
      return "Cost Z-Score";
    case "cost_ratio_p95":
      return "Cost / P95";
    case "cost_ratio_mean":
      return "Cost / Mean";
    case "daily_spend_zscore":
      return "Daily Spend Z";
    case "cost_per_unit_ratio":
      return "Cost/Unit Ratio";
    case "error_count":
      return "Error Count";
    default:
      return key;
  }
}

// ── Detail Drawer ───────────────────────────────────────────────────────────

function SignalBar({
  label,
  value,
  threshold,
}: {
  label: string;
  value: number;
  threshold: number;
}) {
  const isExceeded = value > threshold;
  const barWidth = Math.min(Math.abs(value) / (threshold * 2 || 1), 1) * 100;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span
          className={cn(
            "font-mono font-medium",
            isExceeded ? "text-red-600 dark:text-red-400" : "text-foreground",
          )}
        >
          {typeof value === "number" ? value.toFixed(2) : "—"}
          <span className="text-muted-foreground ml-1 font-normal">
            (threshold: {threshold})
          </span>
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-300",
            isExceeded ? "bg-red-500" : "bg-muted-foreground/30",
          )}
          style={{ width: `${Math.min(barWidth, 100)}%` }}
        />
      </div>
    </div>
  );
}

function ExplanationDrawer({
  anomaly,
  open,
  onClose,
}: {
  anomaly: Anomaly | null;
  open: boolean;
  onClose: () => void;
}) {
  const [showRaw, setShowRaw] = React.useState(false);
  const explanation: AnomalyExplanation | null | undefined = anomaly?.explanation;

  const signals = React.useMemo(() => {
    if (!explanation) return [];
    return [
      { key: "cost_zscore", value: explanation.cost_zscore ?? 0 },
      { key: "cost_ratio_p95", value: explanation.cost_ratio_p95 ?? 0 },
      { key: "cost_ratio_mean", value: explanation.cost_ratio_mean ?? 0 },
      { key: "daily_spend_zscore", value: explanation.daily_spend_zscore ?? 0 },
      { key: "cost_per_unit_ratio", value: explanation.cost_per_unit_ratio ?? 0 },
      { key: "error_count", value: explanation.error_count ?? 0 },
    ];
  }, [explanation]);

  const score = anomaly?.anomaly_score ?? anomaly?.anomaly_score ?? 0;

  return (
    <Sheet open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <SheetContent side="right" className="sm:max-w-md w-full">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <span
              className={cn(
                "inline-flex items-center justify-center rounded px-1.5 py-0.5 text-xs font-mono font-bold",
                scoreColor(score),
              )}
            >
              {(score * 100).toFixed(0)}%
            </span>
            {anomaly?.service ?? "Unknown"}
          </SheetTitle>
          <SheetDescription>
            {anomaly?.region && `${anomaly.region} · `}
            {formatCurrency(anomaly?.cost ?? anomaly?.cost_value)}
            {anomaly?.date && ` · ${new Date(anomaly.date).toLocaleString()}`}
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="flex-1 px-4 pb-4">
          {!explanation ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              Explanation unavailable for historical records
            </div>
          ) : (
            <div className="space-y-6 pt-2">
              {/* Explanation summary */}
              <div className="rounded-lg border border-orange-200 bg-orange-50 p-3 text-sm text-orange-900 dark:border-orange-900/30 dark:bg-orange-950/20 dark:text-orange-300">
                <p className="font-medium text-xs uppercase tracking-wide text-orange-700 dark:text-orange-400 mb-1">
                  Why this was flagged
                </p>
                {explanation.human_readable}
              </div>

              {/* Signal breakdown */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
                  Signal Breakdown
                </h4>
                <div className="space-y-3">
                  {signals.map((s) => (
                    <SignalBar
                      key={s.key}
                      label={signalLabel(s.key)}
                      value={s.value}
                      threshold={signalThreshold(s.key)}
                    />
                  ))}
                </div>
              </div>

              {/* Raw JSON */}
              <div>
                <button
                  onClick={() => setShowRaw(!showRaw)}
                  className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showRaw ? (
                    <ChevronUp className="size-3" />
                  ) : (
                    <ChevronDown className="size-3" />
                  )}
                  Raw explanation JSON
                </button>
                {showRaw && (
                  <pre className="mt-2 rounded-lg bg-muted p-3 text-xs font-mono overflow-x-auto">
                    {JSON.stringify(explanation, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}

// ── Filter chips popover ────────────────────────────────────────────────────

function FilterPopover({
  activeFilters,
  onToggle,
  onClear,
}: {
  activeFilters: Set<string>;
  onToggle: (param: string) => void;
  onClear: () => void;
}) {
  const [open, setOpen] = React.useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        className="inline-flex h-7 items-center justify-start gap-1.5 rounded-md border bg-background px-2.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
      >
        <Filter className="size-3" />
        Filters
        {activeFilters.size > 0 && (
          <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
            {activeFilters.size}
          </Badge>
        )}
      </PopoverTrigger>
      <PopoverContent className="w-72 p-3" align="start">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Filter anomalies</span>
            {activeFilters.size > 0 && (
              <button onClick={onClear} className="text-[10px] text-muted-foreground hover:text-foreground">
                Clear all
              </button>
            )}
          </div>
          {FILTER_CHIPS.map((chip) => {
            const active = activeFilters.has(chip.param);
            return (
              <button
                key={chip.param}
                onClick={() => onToggle(chip.param)}
                className={cn(
                  "w-full text-left flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors",
                  active
                    ? "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <span
                  className={cn(
                    "size-3.5 rounded-sm border flex items-center justify-center",
                    active
                      ? "bg-orange-500 border-orange-500"
                      : "border-muted-foreground/30",
                  )}
                >
                  {active && <span className="size-1.5 rounded-sm bg-white" />}
                </span>
                {chip.label}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// ── Anomaly row (table-style) ───────────────────────────────────────────────

function AnomalyRow({
  a,
  idx,
  reduced,
  onSelect,
}: {
  a: Anomaly;
  idx: number;
  reduced: boolean;
  onSelect: (a: Anomaly) => void;
}) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    const delay = idx < 5 ? staggerDelay(idx, 40) : 0;
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [idx]);

  const score = a.anomaly_score ?? 0;
  const explanation = a.explanation;
  const cost = a.cost ?? a.cost_value ?? 0;

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(a)}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onSelect(a); }}
      className={cn(
        "grid grid-cols-[auto_1fr_auto] gap-3 rounded-lg border border-border/50 bg-background/50 p-3 transition-all duration-100 hover:bg-muted/50 hover:border-border cursor-pointer",
        !visible && "opacity-0 translate-y-2",
        visible && "opacity-100 translate-y-0",
      )}
      style={{
        transitionTimingFunction: "var(--ease-out-expo)",
        transitionDuration: "250ms",
      }}
    >
      {/* Score badge */}
      <div
        className={cn(
          "flex size-10 shrink-0 items-center justify-center rounded-lg font-mono text-xs font-bold",
          scoreColor(score),
        )}
      >
        {(score * 100).toFixed(0)}
      </div>

      {/* Content */}
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium">
            {a.service || "Unknown"}
            {a.region && (
              <span className="text-muted-foreground"> · {a.region}</span>
            )}
          </span>
        </div>

        {/* Human-readable explanation */}
        <div className="mt-1 text-xs text-muted-foreground line-clamp-2">
          {explanation?.human_readable
            ? truncate(explanation.human_readable, 80)
            : "Explanation unavailable"}
        </div>

        {/* Signal pills — hidden on mobile */}
        {explanation && (
          <div className="mt-2 hidden sm:flex flex-wrap gap-1">
            {explanation.cost_zscore != null && (
              <span
                className={cn(
                  "inline-flex items-center rounded px-1.5 py-0.5 font-mono text-[10px] font-medium",
                  Math.abs(explanation.cost_zscore) > 3
                    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    : "bg-muted text-muted-foreground",
                )}
              >
                z={explanation.cost_zscore.toFixed(1)}
              </span>
            )}
            {explanation.cost_ratio_p95 != null && (
              <span
                className={cn(
                  "inline-flex items-center rounded px-1.5 py-0.5 font-mono text-[10px] font-medium",
                  explanation.cost_ratio_p95 > 2
                    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    : "bg-muted text-muted-foreground",
                )}
              >
                p95={explanation.cost_ratio_p95.toFixed(1)}×
              </span>
            )}
          </div>
        )}

        {/* Cost */}
        <div className="mt-2 flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-mono">
            {formatCurrency(cost, { currency: "USD" })}
          </Badge>
        </div>
      </div>

      {/* Severity + chevron */}
      <div className="flex flex-col items-end justify-between">
        <Badge variant={severityVariant(a.severity)} className="whitespace-nowrap">
          {a.severity ?? "low"}
        </Badge>
        <span className="text-xs text-muted-foreground">→</span>
      </div>
    </div>
  );
}

// ── Main panel ──────────────────────────────────────────────────────────────

export function AnomalyPanel() {
  const [activeFilters, setActiveFilters] = React.useState<Set<string>>(new Set());
  const [selectedAnomaly, setSelectedAnomaly] = React.useState<Anomaly | null>(null);
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const reduced = useReducedMotion();

  // Build API filter params from active chips
  const filterParams = React.useMemo<AnomalyFilterParams>(() => {
    const params: AnomalyFilterParams = {};
    for (const chip of FILTER_CHIPS) {
      if (activeFilters.has(chip.param)) {
        (params as any)[chip.param] = chip.value;
      }
    }
    return params;
  }, [activeFilters]);

  const q = useAnomalies(filterParams);

  const toggleFilter = (param: string) => {
    setActiveFilters((prev) => {
      const next = new Set(prev);
      if (next.has(param)) {
        next.delete(param);
      } else {
        next.add(param);
      }
      return next;
    });
  };

  const clearFilters = () => setActiveFilters(new Set());

  const openDrawer = (a: Anomaly) => {
    setSelectedAnomaly(a);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setTimeout(() => setSelectedAnomaly(null), 200);
  };

  const anomalies: Anomaly[] = Array.isArray(q.data) ? q.data : q.data?.anomalies ?? [];
  const highCount = anomalies.filter((a) => a.severity === "high").length;
  const mediumCount = anomalies.filter((a) => a.severity === "medium").length;

  return (
    <>
      <Card className="relative overflow-hidden border-border/50 bg-card shadow-sm h-full">
        <CardHeader className="relative flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TriangleAlert className="size-4 text-orange-500" />
              Anomalies
            </CardTitle>
            <CardDescription>
              {activeFilters.size > 0
                ? "Filtered anomaly view"
                : "Detected cost anomalies"}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <FilterPopover
              activeFilters={activeFilters}
              onToggle={toggleFilter}
              onClear={clearFilters}
            />
            <Badge variant="outline" className="text-xs">
              {q.data?.total_count ?? anomalies.length ?? 0}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="relative space-y-4">
          {/* Summary stats */}
          {!q.isLoading && anomalies.length > 0 && (
            <div className="flex items-center gap-3 text-xs">
              {highCount > 0 && (
                <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                  <span className="size-1.5 rounded-full bg-red-500" />
                  {highCount} high
                </span>
              )}
              {mediumCount > 0 && (
                <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                  <span className="size-1.5 rounded-full bg-amber-500" />
                  {mediumCount} medium
                </span>
              )}
              <span className="flex items-center gap-1 text-muted-foreground">
                <span className="size-1.5 rounded-full bg-muted-foreground/30" />
                {anomalies.length - highCount - mediumCount} low
              </span>
            </div>
          )}

          {/* Loading */}
          {q.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          ) : q.isError ? (
            <div className="text-sm text-destructive">Failed to load anomalies.</div>
          ) : anomalies.length === 0 ? (
            <div className="text-sm text-muted-foreground">No anomalies detected. Great job!</div>
          ) : (
            /* Anomaly list */
            <div className="space-y-2">
              {anomalies.slice(0, 15).map((a: Anomaly, idx: number) => (
                <AnomalyRow
                  key={String(a.id ?? idx)}
                  a={a}
                  idx={idx}
                  reduced={reduced}
                  onSelect={openDrawer}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detail drawer */}
      <ExplanationDrawer
        anomaly={selectedAnomaly}
        open={drawerOpen}
        onClose={closeDrawer}
      />
    </>
  );
}
