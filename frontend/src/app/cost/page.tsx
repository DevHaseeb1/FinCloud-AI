"use client";

import * as React from "react";
import { Download, BarChart3 } from "lucide-react";
import { DateRangePicker } from "@/components/filters/DateRangePicker";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart } from "@/components/charts/LineChart";
import { useCostTimeseries } from "@/hooks/useCost";
import { formatCurrency } from "@/lib/format";

type Range = { from?: Date; to?: Date };

function toISO(d?: Date) {
  if (!d) return undefined;
  return d.toISOString().slice(0, 10);
}

function downloadCsv(rows: Array<{ date: string; cost: number }>) {
  const header = "date,cost\n";
  const body = rows.map((r) => `${r.date},${r.cost}`).join("\n");
  const blob = new Blob([header + body], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cost-timeseries.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export default function CostPage() {
  const [range, setRange] = React.useState<Range>({});
  const [service, setService] = React.useState<string>("all");
  const [region, setRegion] = React.useState<string>("all");

  const q = useCostTimeseries({
    start: toISO(range.from),
    end: toISO(range.to),
    service: service === "all" ? undefined : service,
    region: region === "all" ? undefined : region,
  });

  const currency = "USD";
  const totalCost = q.data?.reduce((sum: number, d: { cost: number }) => sum + d.cost, 0) ?? 0;
  const avgCost = q.data && q.data.length > 0 ? totalCost / q.data.length : 0;

  return (
    <div className="space-y-8 pb-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="size-8" />
          Cost Analytics
        </h1>
        <p className="text-muted-foreground">
          Analyze cloud spending trends with filters and export capabilities.
        </p>
      </div>

      {/* Filters */}
      <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
        <div className="absolute -right-32 -top-32 size-64 rounded-full bg-purple-500/5 blur-3xl" />
        <CardHeader className="relative">
          <CardTitle>Filters</CardTitle>
          <CardDescription>Customize your cost analysis view</CardDescription>
        </CardHeader>
        <CardContent className="relative">
          <div className="grid gap-4 md:grid-cols-5">
            <div>
              <DateRangePicker value={range} onChange={setRange} />
            </div>
            <Select value={service} onValueChange={(v) => setService(v ?? "all")}>
              <SelectTrigger>
                <SelectValue placeholder="Service" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All services</SelectItem>
                <SelectItem value="ec2">EC2</SelectItem>
                <SelectItem value="s3">S3</SelectItem>
                <SelectItem value="rds">RDS</SelectItem>
                <SelectItem value="lambda">Lambda</SelectItem>
              </SelectContent>
            </Select>
            <Select value={region} onValueChange={(v) => setRegion(v ?? "all")}>
              <SelectTrigger>
                <SelectValue placeholder="Region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All regions</SelectItem>
                <SelectItem value="us-east-1">us-east-1</SelectItem>
                <SelectItem value="us-west-2">us-west-2</SelectItem>
                <SelectItem value="eu-west-1">eu-west-1</SelectItem>
                <SelectItem value="ap-southeast-1">ap-southeast-1</SelectItem>
              </SelectContent>
            </Select>
            <div className="md:col-span-2 md:text-right">
              <Button
                variant="outline"
                onClick={() => downloadCsv((q.data ?? []) as any)}
                disabled={!q.data || q.data.length === 0}
                className="w-full md:w-auto"
              >
                <Download className="mr-2 size-4" />
                Export CSV
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      {q.data && q.data.length > 0 && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Total Cost</div>
              <div className="text-2xl font-bold mt-2">{formatCurrency(totalCost, { currency })}</div>
            </CardContent>
          </Card>
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Average Daily Cost</div>
              <div className="text-2xl font-bold mt-2">{formatCurrency(avgCost, { currency })}</div>
            </CardContent>
          </Card>
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Data Points</div>
              <div className="text-2xl font-bold mt-2">{q.data.length}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Chart */}
      <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm">
        <div className="absolute -right-32 -top-32 size-64 rounded-full bg-blue-500/5 blur-3xl" />
        <CardHeader className="relative">
          <CardTitle>Cost Trend</CardTitle>
          <CardDescription>Daily cost analysis with filters applied</CardDescription>
        </CardHeader>
        <CardContent className="relative">
          {q.isLoading ? (
            <Skeleton className="h-64 w-full rounded-lg" />
          ) : q.isError ? (
            <div className="text-sm text-destructive">Failed to load cost data.</div>
          ) : (q.data?.length ?? 0) === 0 ? (
            <div className="text-sm text-muted-foreground">No data for selected filters.</div>
          ) : (
            <LineChart
              data={q.data ?? []}
              xKey="date"
              yKey="cost"
              yFormatter={(v) => formatCurrency(v, { currency })}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

