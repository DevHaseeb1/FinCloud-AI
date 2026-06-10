"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { uploadService } from "@/services/uploadService";
import { useDataMode } from "@/lib/mode";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CloudUpload, CheckCircle2, AlertCircle, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

export default function UploadPage() {
  const { mode } = useDataMode();
  const [file, setFile] = React.useState<File | null>(null);
  const [dragActive, setDragActive] = React.useState(false);
  const [successVisible, setSuccessVisible] = React.useState(false);
  const reduced = useReducedMotion();

  const m = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("Please choose a CSV file.");
      return uploadService.uploadCsv(file, { mode });
    },
    onSuccess: (data) => {
      toast.success("Upload Complete!", {
        description: `Successfully ingested ${data?.rows_ingested ?? 0} rows from your CSV file.`,
      });
      setFile(null);
      setSuccessVisible(true);
      setTimeout(() => setSuccessVisible(false), 3000);
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
          Import your cost data via CSV to begin cost analysis and anomaly detection.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
            <div className="absolute -right-32 -top-32 size-64 rounded-full bg-cyan/5 blur-3xl pointer-events-none" />
            <CardHeader className="relative">
              <CardTitle className="flex items-center gap-2">
                <CloudUpload className="size-5 text-cyan" />
                Upload CSV File
              </CardTitle>
              <CardDescription>Drag and drop your CSV file or click to select</CardDescription>
            </CardHeader>
            <CardContent className="relative space-y-6">
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={cn(
                  "relative rounded-xl border-2 border-dashed transition-all duration-100 p-8 text-center",
                  !reduced && !dragActive && "animate-upload-ring-pulse",
                  dragActive
                    ? "border-cyan bg-cyan/5"
                    : "border-border/50 bg-background/50",
                  m.isError && "animate-[shake_400ms_ease-in-out]",
                )}
                style={{
                  borderColor: dragActive ? "var(--cyan)" : undefined,
                  transitionTimingFunction: dragActive ? "var(--ease-spring)" : undefined,
                }}
              >
                <div className="space-y-3">
                  <div
                    className="flex justify-center transition-all duration-200"
                    style={{
                      transform: dragActive ? "translateY(-6px)" : "translateY(0)",
                      transitionTimingFunction: dragActive ? "var(--ease-spring)" : undefined,
                    }}
                  >
                    <Upload className={cn("size-12", dragActive ? "text-cyan" : "text-muted-foreground")} />
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

              {successVisible && (
                <div
                  className="flex items-center gap-3 rounded-lg border border-green-500/50 bg-green-500/10 p-4 transition-all duration-300"
                  style={{ transitionTimingFunction: "var(--ease-spring)" }}
                >
                  <CheckCircle2 className="size-5 text-green-500 transition-transform duration-300"
                    style={{
                      transform: "scale(1)",
                      transitionTimingFunction: "var(--ease-spring)",
                    }}
                  />
                  <div>
                    <div className="text-sm font-medium text-green-600 dark:text-green-400">
                      Upload successful!
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Data is being processed
                    </div>
                  </div>
                </div>
              )}

              <Button
                size="lg"
                onClick={() => m.mutate()}
                disabled={!file || m.isPending}
                className="w-full transition-all duration-100 active:scale-[0.98]"
              >
                {m.isPending ? (
                  <>
                    <svg className="animate-spin size-4 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span className="animate-pulse">Uploading...</span>
                    {!reduced && (
                      <span className="ml-2 h-1.5 flex-1 rounded-full bg-primary-foreground/20 overflow-hidden">
                        <span className="block h-full bg-primary-foreground/60 rounded-full transition-all duration-300 animate-pulse" style={{ width: '60%' }} />
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    <CloudUpload className="size-4 mr-2" />
                    Upload CSV
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden border-border/50 bg-surface/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg">Example CSV Format</CardTitle>
              <CardDescription>Your CSV should have these required columns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border/50">
                      <th className="text-left py-2 px-3 font-medium font-mono">timestamp</th>
                      <th className="text-left py-2 px-3 font-medium font-mono">service</th>
                      <th className="text-left py-2 px-3 font-medium font-mono">region</th>
                      <th className="text-left py-2 px-3 font-medium font-mono">total_cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">2024-01-01T00:00:00</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">ec2</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">us-east-1</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">285.50</td>
                    </tr>
                    <tr>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">2024-01-02T00:00:00</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">s3</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">us-west-2</td>
                      <td className="py-2 px-3 text-muted-foreground font-mono text-xs">150.25</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

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

          <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-cyan/10 via-card/30 to-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertCircle className="size-4 text-cyan" />
                Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex gap-2">
                <span className="text-cyan font-bold">→</span>
                <span>Include multiple records for better anomaly detection</span>
              </div>
              <div className="flex gap-2">
                <span className="text-cyan font-bold">→</span>
                <span>Daily timestamps work best for analysis</span>
              </div>
              <div className="flex gap-2">
                <span className="text-cyan font-bold">→</span>
                <span>Ensure cost values are numeric</span>
              </div>
              <div className="flex gap-2">
                <span className="text-cyan font-bold">→</span>
                <span>Duplicate entries will be handled by the system</span>
              </div>
            </CardContent>
          </Card>

          {m.isPending && (
            <Card className="border-cyan/50 bg-cyan/5">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-sm">
                  <div className="animate-spin">
                    <CloudUpload className="size-4 text-cyan" />
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
            <Card className="border-ember/50 bg-ember/5">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-sm text-ember">
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
