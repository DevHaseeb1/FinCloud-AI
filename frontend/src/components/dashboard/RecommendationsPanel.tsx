"use client";

import * as React from "react";
import { Sparkles, CheckCircle2, AlertCircle, ArrowUpDown, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecommendations } from "@/hooks/useRecommendations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useCountUp, staggerDelay } from "@/lib/animations";
import { formatCurrency } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Recommendation } from "@/types/apiTypes";

type SortKey = "savings" | "priority" | "category";

const PRIORITY_ORDER: Record<string, number> = { high: 0, medium: 1, low: 2 };

function priorityIcon(priority?: string) {
  if (priority === "high") return <AlertCircle className="size-4 text-red-500/70" />;
  if (priority === "medium") return <CheckCircle2 className="size-4 text-amber-500/70" />;
  return <CheckCircle2 className="size-4 text-emerald-500/70" />;
}

function priorityVariant(priority?: string) {
  if (priority === "high") return "destructive";
  if (priority === "medium") return "secondary";
  return "outline";
}

function SortButton({ label, sortKey, currentSort, onSort }: { label: string; sortKey: SortKey; currentSort: { key: SortKey; asc: boolean }; onSort: (key: SortKey) => void }) {
  const active = currentSort.key === sortKey;
  return (
    <button
      onClick={() => onSort(sortKey)}
      className={cn(
        "flex items-center gap-1 text-xs font-medium transition-colors",
        active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
      )}
    >
      {label}
      <ArrowUpDown className={cn("size-3", active && "text-cyan")} />
    </button>
  );
}

export function RecommendationsPanel() {
  const q = useRecommendations();
  const reduced = useReducedMotion();
  const currency = "USD";
  const [sort, setSort] = React.useState<{ key: SortKey; asc: boolean }>({ key: "savings", asc: false });

  const totalSavings = q.data?.reduce((sum: number, r: Recommendation) => sum + (r.estimated_savings ?? 0), 0) ?? 0;
  const highPriorityCount = q.data?.filter((r: Recommendation) => r.priority === "high").length ?? 0;
  const countedTotal = useCountUp(totalSavings, 800, reduced);

  const sorted = React.useMemo(() => {
    if (!q.data) return [];
    return [...q.data].sort((a: Recommendation, b: Recommendation) => {
      let cmp = 0;
      if (sort.key === "savings") {
        cmp = (a.estimated_savings ?? 0) - (b.estimated_savings ?? 0);
      } else if (sort.key === "priority") {
        cmp = (PRIORITY_ORDER[a.priority ?? "low"] ?? 2) - (PRIORITY_ORDER[b.priority ?? "low"] ?? 2);
      } else {
        cmp = (a.category ?? "").localeCompare(b.category ?? "");
      }
      return sort.asc ? cmp : -cmp;
    });
  }, [q.data, sort]);

  const handleSort = (key: SortKey) => {
    setSort((prev) => ({
      key,
      asc: prev.key === key ? !prev.asc : key === "category",
    }));
  };

  return (
    <Card className="relative overflow-hidden border-border/50 bg-card shadow-sm">
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="size-4 text-cyan" />
              Recommendations
            </CardTitle>
            <CardDescription>Optimization opportunities to reduce costs</CardDescription>
          </div>
          {totalSavings > 0 && (
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Potential Savings</div>
              <div className="text-lg font-semibold text-emerald-600 dark:text-emerald-400 font-mono">
                {formatCurrency(countedTotal, { currency })}
              </div>
            </div>
          )}
        </div>
        {highPriorityCount > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <Badge variant="destructive" className="text-xs">
              {highPriorityCount} high-priority
            </Badge>
            <span className="text-xs text-muted-foreground">
              Action required to reduce costs
            </span>
          </div>
        )}
      </CardHeader>
      <CardContent className="relative">
        {q.isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load recommendations.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No recommendations available yet.</div>
        ) : (
          <>
            {/* Desktop: table layout */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/50">
                    <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Recommendation</th>
                    <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Category</th>
                    <th className="pb-3 text-left">
                      <SortButton label="Priority" sortKey="priority" currentSort={sort} onSort={handleSort} />
                    </th>
                    <th className="pb-3 text-right">
                      <SortButton label="Savings" sortKey="savings" currentSort={sort} onSort={handleSort} />
                    </th>
                    <th className="pb-3 text-right text-xs font-medium text-muted-foreground">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.slice(0, 5).map((r: Recommendation, idx: number) => (
                    <RecommendationRow key={String(r.id ?? idx)} r={r} idx={idx} currency={currency} reduced={reduced} />
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile: card layout */}
            <div className="md:hidden space-y-2">
              {sorted.slice(0, 4).map((r: Recommendation, idx: number) => (
                <RecommendationCard key={String(r.id ?? idx)} r={r} idx={idx} currency={currency} reduced={reduced} />
              ))}
            </div>

            {(q.data?.length ?? 0) > 5 && (
              <div className="mt-3 flex justify-center">
                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground gap-1">
                  View all {q.data?.length} recommendations
                  <ExternalLink className="size-3" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

function RecommendationRow({
  r,
  idx,
  currency,
  reduced,
}: {
  r: Recommendation;
  idx: number;
  currency: string;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);
  const counted = useCountUp(r.estimated_savings ?? 0, 800, reduced);

  React.useEffect(() => {
    const timer = setTimeout(() => setVisible(true), staggerDelay(idx, 40));
    return () => clearTimeout(timer);
  }, [idx]);

  return (
    <tr
      className={cn(
        "border-b border-border/30 transition-colors hover:bg-muted/30",
        !visible && "opacity-0",
        visible && "opacity-100",
      )}
      style={{
        transitionTimingFunction: "var(--ease-out-expo)",
        transitionDuration: "300ms",
      }}
    >
      <td className="py-3 pr-4">
        <div className="flex items-center gap-2">
          {priorityIcon(r.priority)}
          <div>
            <div className="font-medium">{r.title ?? "Optimization"}</div>
            {r.description && (
              <div className="text-xs text-muted-foreground line-clamp-1 max-w-xs">{r.description}</div>
            )}
          </div>
        </div>
      </td>
      <td className="py-3 pr-4">
        {r.category && (
          <Badge variant="outline" className="text-xs">{r.category}</Badge>
        )}
      </td>
      <td className="py-3 pr-4">
        <Badge variant={priorityVariant(r.priority) as any} className="whitespace-nowrap text-xs">
          {r.priority ?? "low"}
        </Badge>
      </td>
      <td className="py-3 pr-4 text-right">
        {typeof r.estimated_savings === "number" && (
          <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">
            {formatCurrency(counted, { currency })}<span className="text-xs text-muted-foreground font-normal">/mo</span>
          </span>
        )}
      </td>
      <td className="py-3 text-right">
        <Button variant="ghost" size="sm" className="text-xs h-7">
          Apply
        </Button>
      </td>
    </tr>
  );
}

function RecommendationCard({
  r,
  idx,
  currency,
  reduced,
}: {
  r: Recommendation;
  idx: number;
  currency: string;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);
  const counted = useCountUp(r.estimated_savings ?? 0, 800, reduced);

  React.useEffect(() => {
    const timer = setTimeout(() => setVisible(true), staggerDelay(idx, 40));
    return () => clearTimeout(timer);
  }, [idx]);

  return (
    <div
      className={cn(
        "rounded-lg border border-border/50 bg-background/50 p-3 transition-all duration-200 hover:bg-muted/30",
        !visible && "opacity-0 translate-y-2",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          {priorityIcon(r.priority)}
          <div className="min-w-0">
            <div className="text-sm font-medium truncate">{r.title ?? "Optimization"}</div>
            {r.description && (
              <div className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{r.description}</div>
            )}
          </div>
        </div>
        <Badge variant={priorityVariant(r.priority) as any} className="shrink-0 text-[10px]">
          {r.priority ?? "low"}
        </Badge>
      </div>
      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {r.category && <Badge variant="outline" className="text-[10px]">{r.category}</Badge>}
          {typeof r.estimated_savings === "number" && (
            <span className="font-mono text-xs font-semibold text-emerald-600 dark:text-emerald-400">
              {formatCurrency(counted, { currency })}/mo
            </span>
          )}
        </div>
        <Button variant="ghost" size="sm" className="text-[10px] h-6 px-2">
          Apply
        </Button>
      </div>
    </div>
  );
}
