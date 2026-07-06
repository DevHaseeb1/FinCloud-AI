"use client";

import * as React from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { ChartTooltip } from "@/components/charts/ChartTooltip";

export function LineChart({
  data,
  xKey,
  yKey,
  yFormatter,
}: {
  data: Array<Record<string, any>>;
  xKey: string;
  yKey: string;
  yFormatter?: (v: number) => string;
}) {
  const reduced = useReducedMotion();

  const avg = data.length > 0
    ? data.reduce((sum: number, d: Record<string, any>) => sum + (d[yKey] ?? 0), 0) / data.length
    : 0;

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
          <defs>
            <linearGradient id="costFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--cyan)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="var(--cyan)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.15}
            stroke="var(--border)"
          />
          <XAxis
            dataKey={xKey}
            tickMargin={8}
            minTickGap={24}
            stroke="var(--muted-foreground)"
            style={{ fontSize: "11px", fill: "var(--muted-foreground)" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={yFormatter}
            width={70}
            stroke="var(--muted-foreground)"
            style={{ fontSize: "11px", fill: "var(--muted-foreground)" }}
            tickLine={false}
            axisLine={false}
          />
          {avg > 0 && (
            <ReferenceLine
              y={avg}
              stroke="var(--muted-foreground)"
              strokeDasharray="4 4"
              strokeOpacity={0.4}
            />
          )}
          <Tooltip
            content={<ChartTooltip valueFormatter={yFormatter} />}
            cursor={{ stroke: "var(--cyan)", strokeWidth: 1, strokeDasharray: "4 4" }}
          />
          <Area
            type="monotone"
            dataKey={yKey}
            stroke="var(--cyan)"
            strokeWidth={2}
            fill="url(#costFill)"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2, stroke: "var(--cyan)", fill: "var(--background)" }}
            isAnimationActive={!reduced}
            animationDuration={1200}
            animationEasing="ease-out"
            name="Cost"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
