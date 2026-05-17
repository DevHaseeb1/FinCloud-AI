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
        <AreaChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
          <defs>
            <linearGradient id="colorBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
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

          {hasBand ? (
            <>
              <Area
                type="monotone"
                dataKey={upperKey as string}
                stroke="transparent"
                fill="url(#colorBand)"
                isAnimationActive={true}
              />
              <Area
                type="monotone"
                dataKey={lowerKey as string}
                stroke="transparent"
                fill="hsl(var(--background))"
                fillOpacity={1}
                isAnimationActive={true}
              />
            </>
          ) : null}

          <Line
            type="monotone"
            dataKey={predictedKey}
            stroke="hsl(var(--primary))"
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            name="Predicted"
          />
          {actualKey && (
            <Line
              type="monotone"
              dataKey={actualKey}
              stroke="hsl(var(--muted-foreground))"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
              strokeDasharray="5 5"
              name="Actual"
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

