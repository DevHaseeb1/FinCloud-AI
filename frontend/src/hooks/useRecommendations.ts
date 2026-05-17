"use client";

import { useQuery } from "@tanstack/react-query";
import { recommendationService } from "@/services/recommendationService";
import { useDataMode } from "@/lib/mode";
import type { Recommendation } from "@/types/apiTypes";

type RawRecommendation = Recommendation & {
  suggestion?: string;
  recommendation_type?: string;
};

export function useRecommendations() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["recommendations", "list", mode],
    queryFn: async () => {
      const data = await recommendationService.list({ mode });
      // Unwrap if nested in recommendations object
      const recommendations = Array.isArray(data) ? data : data?.recommendations ?? [];
      // Map API field names to component field names
      return (recommendations as RawRecommendation[]).map((r) => ({
        ...r,
        title: r.suggestion ?? r.title,
        category: r.recommendation_type ?? r.category,
      }));
    },
  });
}

