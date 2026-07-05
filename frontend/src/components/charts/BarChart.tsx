"use client";

import {
  Bar,
  BarChart as RBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { ChartTooltip } from "@/components/charts/ChartTooltip";

export function BarChart({
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
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RBarChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
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
          <Tooltip
            content={<ChartTooltip valueFormatter={yFormatter} />}
            cursor={{ fill: "var(--muted)", opacity: 0.3 }}
          />
          <Bar
            dataKey={yKey}
            fill="var(--cyan)"
            radius={[4, 4, 0, 0]}
            isAnimationActive={!reduced}
            animationDuration={600}
            animationEasing="ease-out"
          />
        </RBarChart>
      </ResponsiveContainer>
    </div>
  );
}
