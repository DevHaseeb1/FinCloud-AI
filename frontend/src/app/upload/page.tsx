"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { uploadService } from "@/services/uploadService";
import { useDataMode } from "@/lib/mode";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";

export default function UploadPage() {
  const { mode } = useDataMode();
  const [file, setFile] = React.useState<File | null>(null);

  const m = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("Please choose a CSV file.");
      return uploadService.uploadCsv(file, { mode });
    },
    onSuccess: (data) => {
      toast.success("Upload complete", {
        description: `Ingested ${data?.rows_ingested ?? 0} rows.`,
      });
      setFile(null);
    },
    onError: (err: any) => {
      toast.error("Upload failed", { description: err?.message ?? "Unknown error" });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Upload</h1>
        <p className="text-sm text-muted-foreground">
          Upload a CSV dataset to the backend ingestion pipeline.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Upload CSV</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="file">CSV File</Label>
            <Input
              id="file"
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              disabled={m.isPending}
            />
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={() => m.mutate()} disabled={!file || m.isPending}>
              Upload
            </Button>
            {m.isPending ? <Skeleton className="h-4 w-40" /> : null}
            <div className="text-sm text-muted-foreground">
              Mode: <span className="font-medium">{mode}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

