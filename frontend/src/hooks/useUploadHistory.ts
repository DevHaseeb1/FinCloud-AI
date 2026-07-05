"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadService } from "@/services/uploadService";
import { toast } from "sonner";

export function useUploadHistory() {
  const qc = useQueryClient();

  const q = useQuery({
    queryKey: ["uploaded-files"],
    queryFn: () => uploadService.list(),
  });

  const del = useMutation({
    mutationFn: (id: number) => uploadService.delete(id),
    onSuccess: (data) => {
      toast.success("File deleted", {
        description: `Removed '${data?.filename}' and all associated data.`,
      });
      qc.invalidateQueries({ queryKey: ["uploaded-files"] });
    },
    onError: (err: any) => {
      toast.error("Delete failed", { description: err?.message ?? "Unknown error" });
    },
  });

  return { query: q, delete: del };
}
