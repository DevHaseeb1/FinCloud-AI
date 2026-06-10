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
} from "recharts";
import { useReducedMotion } from "@/hooks/useReducedMotion";

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

  return (
    <div className="h-64 w-full">
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
            opacity={0.2}
            stroke="hsl(var(--border))"
          />
          <XAxis
            dataKey={xKey}
            tickMargin={8}
            minTickGap={24}
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            tickFormatter={yFormatter}
            width={70}
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: "12px" }}
          />
          <Tooltip
            formatter={(v) => (typeof v === "number" ? yFormatter?.(v) ?? v : v)}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "6px",
              color: "hsl(var(--foreground))",
            }}
            labelStyle={{ color: "hsl(var(--foreground))" }}
          />
          <Area
            type="monotone"
            dataKey={yKey}
            stroke="var(--cyan)"
            strokeWidth={2.5}
            fill="url(#costFill)"
            dot={false}
            isAnimationActive={!reduced}
            animationDuration={1200}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
