"use client";

import * as React from "react";
import { FileText, Trash2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useUploadHistory } from "@/hooks/useUploadHistory";
import { formatDistanceToNow } from "date-fns";

function ConfirmDialog({
  open,
  filename,
  onConfirm,
  onCancel,
  loading,
}: {
  open: boolean;
  filename: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="rounded-xl border border-border/50 bg-surface p-6 shadow-xl max-w-sm w-full mx-4">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="size-6 text-ember" />
          <div>
            <div className="font-semibold">Delete file?</div>
            <div className="text-sm text-muted-foreground mt-1">
              This will remove &lsquo;{filename}&rsquo; and all associated data (raw data, processed data, anomalies, forecasts, recommendations).
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="destructive" size="sm" onClick={onConfirm} disabled={loading}>
            {loading ? "Deleting..." : "Delete"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export function UploadHistory() {
  const { query, delete: delMutation } = useUploadHistory();
  const [confirmId, setConfirmId] = React.useState<number | null>(null);

  const files = query.data?.files ?? [];
  const confirmFile = confirmId ? files.find((f) => f.id === confirmId) : null;

  const handleDelete = () => {
    if (confirmId == null) return;
    delMutation.mutate(confirmId, {
      onSettled: () => setConfirmId(null),
    });
  };

  return (
    <>
      <ConfirmDialog
        open={confirmId != null}
        filename={confirmFile?.filename ?? ""}
        onConfirm={handleDelete}
        onCancel={() => setConfirmId(null)}
        loading={delMutation.isPending}
      />

      <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="size-4 text-cyan" />
            Upload History
          </CardTitle>
          <CardDescription>Previously uploaded files</CardDescription>
        </CardHeader>
        <CardContent>
          {query.isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : query.isError ? (
            <div className="text-sm text-destructive">Failed to load upload history.</div>
          ) : files.length === 0 ? (
            <div className="text-sm text-muted-foreground">No uploads yet.</div>
          ) : (
            <div className="space-y-2">
              {files.map((f) => (
                <div
                  key={f.id}
                  className="flex items-center justify-between rounded-lg border border-border/50 bg-background/50 p-3 transition-all duration-100 hover:bg-background/80"
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">{f.filename}</div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                      <span>
                        {f.row_count.toLocaleString()} rows &middot; {(f.file_size / 1024).toFixed(1)} KB
                      </span>
                      <span>&middot;</span>
                      <span>
                        {f.created_at
                          ? formatDistanceToNow(new Date(f.created_at), { addSuffix: true })
                          : ""}
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 ml-2 shrink-0"
                    onClick={() => setConfirmId(f.id)}
                    disabled={delMutation.isPending}
                  >
                    <Trash2 className="size-4 text-muted-foreground hover:text-destructive" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}
