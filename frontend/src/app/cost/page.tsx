"use client";

import * as React from "react";
import { Download } from "lucide-react";
import { DateRangePicker } from "@/components/filters/DateRangePicker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold tracking-tight">Cost Analytics</h1>
        <p className="text-sm text-muted-foreground">Explore costs with filters and export.</p>
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <DateRangePicker value={range} onChange={setRange} />
        <Select value={service} onValueChange={(v) => setService(v ?? "all")}>
          <SelectTrigger className="w-full md:w-56">
            <SelectValue placeholder="Service" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All services</SelectItem>
            <SelectItem value="ec2">EC2</SelectItem>
            <SelectItem value="s3">S3</SelectItem>
            <SelectItem value="rds">RDS</SelectItem>
          </SelectContent>
        </Select>
        <Select value={region} onValueChange={(v) => setRegion(v ?? "all")}>
          <SelectTrigger className="w-full md:w-56">
            <SelectValue placeholder="Region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All regions</SelectItem>
            <SelectItem value="us-east-1">us-east-1</SelectItem>
            <SelectItem value="us-west-2">us-west-2</SelectItem>
            <SelectItem value="eu-west-1">eu-west-1</SelectItem>
          </SelectContent>
        </Select>
        <div className="md:ml-auto">
          <Button
            variant="outline"
            onClick={() => downloadCsv((q.data ?? []) as any)}
            disabled={!q.data || q.data.length === 0}
          >
            <Download className="mr-2 size-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Time Series</CardTitle>
        </CardHeader>
        <CardContent>
          {q.isLoading ? (
            <Skeleton className="h-64 w-full" />
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

