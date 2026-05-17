import { getData } from "@/services/api";
import type { Recommendation, RecommendationsResponse } from "@/types/apiTypes";

export const recommendationService = {
  list: (opts?: { mode?: string }) =>
    getData<Recommendation[] | RecommendationsResponse>("/recommendations", { params: opts }),
};

