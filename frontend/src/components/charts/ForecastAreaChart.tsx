"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function ForecastAreaChart({
  data,
  xKey,
  actualKey,
  predictedKey,
  lowerKey,
  upperKey,
  yFormatter,
}: {
  data: Array<Record<string, any>>;
  xKey: string;
  actualKey: string;
  predictedKey: string;
  lowerKey?: string;
  upperKey?: string;
  yFormatter?: (v: number) => string;
}) {
  const hasBand = Boolean(lowerKey && upperKey);
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
          <XAxis dataKey={xKey} tickMargin={8} minTickGap={24} />
          <YAxis tickFormatter={yFormatter} width={70} />
          <Tooltip formatter={(v) => (typeof v === "number" ? yFormatter?.(v) ?? v : v)} />

          {hasBand ? (
            <>
              <Area
                type="monotone"
                dataKey={upperKey as string}
                stroke="transparent"
                fill="hsl(var(--primary))"
                fillOpacity={0.12}
              />
              <Area
                type="monotone"
                dataKey={lowerKey as string}
                stroke="transparent"
                fill="hsl(var(--background))"
                fillOpacity={1}
              />
            </>
          ) : null}

          <Line
            type="monotone"
            dataKey={predictedKey}
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey={actualKey}
            stroke="hsl(var(--muted-foreground))"
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

