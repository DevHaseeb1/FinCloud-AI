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
        <RBarChart data={data} margin={{ left: 8, right: 8 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
          <XAxis dataKey={xKey} tickMargin={8} minTickGap={24} />
          <YAxis tickFormatter={yFormatter} width={70} />
          <Tooltip formatter={(v) => (typeof v === "number" ? yFormatter?.(v) ?? v : v)} />
          <Bar dataKey={yKey} fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
        </RBarChart>
      </ResponsiveContainer>
    </div>
  );
}

