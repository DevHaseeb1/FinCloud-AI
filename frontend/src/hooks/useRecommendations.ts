"use client";

import { useQuery } from "@tanstack/react-query";
import { recommendationService } from "@/services/recommendationService";
import { useDataMode } from "@/lib/mode";

export function useRecommendations() {
  const { mode } = useDataMode();
  return useQuery({
    queryKey: ["recommendations", "list", mode],
    queryFn: () => recommendationService.list({ mode }),
  });
}

