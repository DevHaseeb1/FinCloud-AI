import { getData } from "@/services/api";
import type { Recommendation } from "@/types/apiTypes";

export const recommendationService = {
  list: (opts?: { mode?: string }) => getData<Recommendation[]>("/recommendations", { params: opts }),
};

