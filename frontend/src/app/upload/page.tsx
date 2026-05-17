"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { uploadService } from "@/services/uploadService";
import { useDataMode } from "@/lib/mode";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { CloudUpload, CheckCircle2, AlertCircle } from "lucide-react";

export default function UploadPage() {
  const { mode } = useDataMode();
  const [file, setFile] = React.useState<File | null>(null);
  const [dragActive, setDragActive] = React.useState(false);

  const m = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("Please choose a CSV file.");
      return uploadService.uploadCsv(file, { mode });
    },
    onSuccess: (data) => {
      toast.success("Upload Complete! ✅", {
        description: `Successfully ingested ${data?.rows_ingested ?? 0} rows from your CSV file.`,
      });
      setFile(null);
    },
    onError: (err: any) => {
      toast.error("Upload Failed", { description: err?.message ?? "Unknown error" });
    },
  });

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles && droppedFiles[0]) {
      setFile(droppedFiles[0]);
    }
  };

  return (
    <div className="space-y-8 pb-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Data Upload</h1>
        <p className="text-muted-foreground">
          Import your AWS cost data via CSV to begin cost analysis and anomaly detection.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Upload Card */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
            <div className="absolute -right-32 -top-32 size-64 rounded-full bg-blue-500/5 blur-3xl" />
            <CardHeader className="relative">
              <CardTitle className="flex items-center gap-2">
                <CloudUpload className="size-5" />
                Upload CSV File
              </CardTitle>
              <CardDescription>Drag and drop your CSV file or click to select</CardDescription>
            </CardHeader>
            <CardContent className="relative space-y-6">
              {/* Drag and Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative rounded-xl border-2 border-dashed transition-all ${
                  dragActive
                    ? "border-primary bg-primary/5"
                    : "border-border/50 bg-background/50"
                } p-8 text-center`}
              >
                <div className="space-y-3">
                  <div className="flex justify-center">
                    <CloudUpload className="size-12 text-muted-foreground" />
                  </div>
                  <div>
                    <Label htmlFor="file" className="text-base font-medium cursor-pointer">
                      Click to upload or drag and drop
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      CSV files up to 100MB
                    </p>
                  </div>
                  <Input
                    id="file"
                    type="file"
                    accept=".csv,text/csv"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                    disabled={m.isPending}
                    className="hidden"
                  />
                </div>
              </div>

              {/* File Preview */}
              {file && (
                <div className="rounded-lg border border-border/50 bg-background/50 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="size-5 text-green-500" />
                      <div>
                        <div className="text-sm font-medium">{file.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {(file.size / 1024).toFixed(2)} KB
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setFile(null)}
                      disabled={m.isPending}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              )}

              {/* Upload Action */}
              <Button
                size="lg"
                onClick={() => m.mutate()}
                disabled={!file || m.isPending}
                className="w-full"
              >
                {m.isPending ? (
                  <>
                    <Skeleton className="h-4 w-4 mr-2" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <CloudUpload className="size-4 mr-2" />
                    Upload CSV
                  </>
                )}
              </Button>

              {/* Mode Info */}
              <div className="flex items-center justify-between pt-4 border-t border-border/50">
                <span className="text-sm text-muted-foreground">Current Mode:</span>
                <Badge variant="outline">{mode}</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Sample CSV Card */}
          <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg">Example CSV Format</CardTitle>
              <CardDescription>Your CSV should have these required columns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border/50">
                      <th className="text-left py-2 px-3 font-medium">timestamp</th>
                      <th className="text-left py-2 px-3 font-medium">service</th>
                      <th className="text-left py-2 px-3 font-medium">region</th>
                      <th className="text-left py-2 px-3 font-medium">total_cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-3 text-muted-foreground">2024-01-01T00:00:00</td>
                      <td className="py-2 px-3 text-muted-foreground">ec2</td>
                      <td className="py-2 px-3 text-muted-foreground">us-east-1</td>
                      <td className="py-2 px-3 text-muted-foreground">285.50</td>
                    </tr>
                    <tr>
                      <td className="py-2 px-3 text-muted-foreground">2024-01-02T00:00:00</td>
                      <td className="py-2 px-3 text-muted-foreground">s3</td>
                      <td className="py-2 px-3 text-muted-foreground">us-west-2</td>
                      <td className="py-2 px-3 text-muted-foreground">150.25</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Info Cards */}
        <div className="space-y-4">
          <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-emerald-500/10 via-card/30 to-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <CheckCircle2 className="size-4 text-emerald-500" />
                Requirements
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                <span>CSV format (.csv)</span>
              </div>
              <div className="flex gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                <span>Required columns: timestamp, service, region, total_cost</span>
              </div>
              <div className="flex gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                <span>Max file size: 100MB</span>
              </div>
              <div className="flex gap-2">
                <span className="text-emerald-500 font-bold">•</span>
                <span>UTF-8 encoding recommended</span>
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-blue-500/10 via-card/30 to-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertCircle className="size-4 text-blue-500" />
                Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex gap-2">
                <span className="text-blue-500 font-bold">→</span>
                <span>Include multiple records for better anomaly detection</span>
              </div>
              <div className="flex gap-2">
                <span className="text-blue-500 font-bold">→</span>
                <span>Daily timestamps work best for analysis</span>
              </div>
              <div className="flex gap-2">
                <span className="text-blue-500 font-bold">→</span>
                <span>Ensure cost values are numeric</span>
              </div>
              <div className="flex gap-2">
                <span className="text-blue-500 font-bold">→</span>
                <span>Duplicate entries will be handled by the system</span>
              </div>
            </CardContent>
          </Card>

          {/* Status Card */}
          {m.isPending && (
            <Card className="border-primary/50 bg-primary/5">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-sm">
                  <div className="animate-spin">
                    <CloudUpload className="size-4" />
                  </div>
                  Uploading your file...
                </div>
              </CardContent>
            </Card>
          )}

          {m.isSuccess && (
            <Card className="border-green-500/50 bg-green-500/5">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-400">
                  <CheckCircle2 className="size-4" />
                  Upload successful!
                </div>
              </CardContent>
            </Card>
          )}

          {m.isError && (
            <Card className="border-red-500/50 bg-red-500/5">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-sm text-red-700 dark:text-red-400">
                  <AlertCircle className="size-4" />
                  {m.error?.message || "Upload failed"}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

