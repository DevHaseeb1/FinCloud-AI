"use client";

import * as React from "react";
import { Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecommendations } from "@/hooks/useRecommendations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useCountUp, staggerDelay } from "@/lib/animations";
import { formatCurrency } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Recommendation } from "@/types/apiTypes";

function priorityIcon(priority?: string) {
  if (priority === "high") return <AlertCircle className="size-4 text-ember/70" />;
  if (priority === "medium") return <CheckCircle2 className="size-4 text-yellow-500/70" />;
  return <CheckCircle2 className="size-4 text-green-500/70" />;
}

function priorityVariant(priority?: string) {
  if (priority === "high") return "destructive";
  if (priority === "medium") return "secondary";
  return "outline";
}

function RecCard({
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
    const timer = setTimeout(() => setVisible(true), staggerDelay(idx, 60));
    return () => clearTimeout(timer);
  }, [idx]);

  return (
    <div
      className={cn(
        "transition-all duration-320",
        !visible && "opacity-0 translate-y-3",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="relative flex items-start gap-3 rounded-lg border border-border/50 bg-background/50 p-3 transition-all duration-100 hover:bg-background/80 hover:border-border group">
        <div className="mt-0.5 flex-shrink-0">
          {priorityIcon(r.priority)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-sm font-medium">{r.title ?? "Optimization"}</div>
          {r.description && (
            <div className="mt-1 text-xs text-muted-foreground line-clamp-2">
              {r.description}
            </div>
          )}
          <div className="mt-2 flex items-center gap-2">
            {typeof r.estimated_savings === "number" && (
              <Badge variant="outline" className="text-xs bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 font-mono">
                Save {formatCurrency(r.estimated_savings, { currency })}/mo
              </Badge>
            )}
            {r.category && (
              <Badge variant="outline" className="text-xs">
                {r.category}
              </Badge>
            )}
          </div>
        </div>
        <div className="flex-shrink-0">
          <Badge variant={priorityVariant(r.priority) as any} className="whitespace-nowrap">
            {r.priority ?? "low"}
          </Badge>
        </div>
      </div>
    </div>
  );
}

export function RecommendationsPanel() {
  const q = useRecommendations();
  const reduced = useReducedMotion();
  const currency = "USD";

  const totalSavings = q.data?.reduce((sum: number, r: Recommendation) => sum + (r.estimated_savings ?? 0), 0) ?? 0;
  const highPriorityCount = q.data?.filter((r: Recommendation) => r.priority === "high").length ?? 0;
  const countedTotal = useCountUp(totalSavings, 800, reduced);

  return (
    <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
      <div className="absolute -right-32 -top-32 size-64 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none" />
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
              <div className="text-sm text-muted-foreground">Potential Savings</div>
              <div className="text-lg font-semibold text-emerald-600 dark:text-emerald-400 font-mono">
                {formatCurrency(countedTotal, { currency })}
              </div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="relative space-y-3">
        {q.isLoading ? (
          <>
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </>
        ) : q.isError ? (
          <div className="text-sm text-destructive">Failed to load recommendations.</div>
        ) : (q.data?.length ?? 0) === 0 ? (
          <div className="text-sm text-muted-foreground">No recommendations available yet.</div>
        ) : (
          <>
            {highPriorityCount > 0 && (
              <div className="rounded-lg bg-ember/10 border border-ember/20 p-3 text-sm">
                <div className="font-medium text-ember">
                  {highPriorityCount} high-priority recommendation{highPriorityCount !== 1 ? "s" : ""}
                </div>
              </div>
            )}
            <div className="space-y-2">
              {q.data?.slice(0, 4).map((r: Recommendation, idx: number) => (
                <RecCard key={String(r.id ?? idx)} r={r} idx={idx} currency={currency} reduced={reduced} />
              ))}
            </div>
            {(q.data?.length ?? 0) > 4 && (
              <div className="text-xs text-muted-foreground text-center pt-2">
                +{(q.data?.length ?? 0) - 4} more recommendations
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
