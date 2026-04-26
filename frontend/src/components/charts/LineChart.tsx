"use client";

import {
  Line,
  LineChart as RLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

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
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RLineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
          <XAxis dataKey={xKey} tickMargin={8} minTickGap={24} />
          <YAxis tickFormatter={yFormatter} width={70} />
          <Tooltip formatter={(v) => (typeof v === "number" ? yFormatter?.(v) ?? v : v)} />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            dot={false}
          />
        </RLineChart>
      </ResponsiveContainer>
    </div>
  );
}

