"use client";

import { useQuery } from "@tanstack/react-query";
import { recommendationService } from "@/services/recommendationService";
import { useDataMode } from "@/lib/mode";
import type { Recommendation } from "@/types/apiTypes";

const PRIORITY_MAP: Record<number, "low" | "medium" | "high"> = {
  1: "high",
  2: "medium",
  3: "low",
  4: "low",
};

function mapPriority(p: unknown): "low" | "medium" | "high" {
  if (typeof p === "number") return PRIORITY_MAP[p] ?? "low";
  if (typeof p === "string" && ["low", "medium", "high"].includes(p)) return p as "low" | "medium" | "high";
  return "low";
}

type RawItem = Record<string, unknown>;

export function useRecommendations() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["recommendations", "list", mode],
    queryFn: async () => {
      const data = await recommendationService.list({ mode });
      const items: RawItem[] = Array.isArray(data) ? data : (data as any)?.recommendations ?? [];
      return items.map((r) => ({
        id: r.id as number | undefined,
        title: (r.suggestion ?? r.title ?? "Optimization") as string,
        description: r.description as string | undefined,
        category: (r.recommendation_type ?? r.category ?? "optimization") as string,
        estimated_savings: r.estimated_savings as number | undefined,
        priority: mapPriority(r.priority),
        confidence_score: r.confidence_score as number | undefined,
        service: r.service as string | undefined,
        region: r.region as string | undefined,
      })) satisfies Recommendation[];
    },
  });
}

