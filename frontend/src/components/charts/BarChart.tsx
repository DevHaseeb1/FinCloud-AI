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
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RBarChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
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
          <Bar 
            dataKey={yKey} 
            fill="hsl(var(--primary))" 
            radius={[6, 6, 0, 0]}
            isAnimationActive={true}
          />
        </RBarChart>
      </ResponsiveContainer>
    </div>
  );
}

