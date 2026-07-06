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
  ReferenceLine,
} from "recharts";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { ChartTooltip } from "@/components/charts/ChartTooltip";

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
  const reduced = useReducedMotion();
  const hasBand = Boolean(lowerKey && upperKey);

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
          <defs>
            <linearGradient id="colorBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--violet)" stopOpacity={0.2} />
              <stop offset="95%" stopColor="var(--violet)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--cyan)" stopOpacity={0.15} />
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
          <Tooltip
            content={<ChartTooltip valueFormatter={yFormatter} />}
            cursor={{ stroke: "var(--violet)", strokeWidth: 1, strokeDasharray: "4 4" }}
          />

          {hasBand ? (
            <>
              <Area
                type="monotone"
                dataKey={upperKey as string}
                stroke="transparent"
                fill="url(#colorBand)"
                isAnimationActive={!reduced}
                animationDuration={800}
                animationEasing="ease-out"
              />
              <Area
                type="monotone"
                dataKey={lowerKey as string}
                stroke="transparent"
                fill="var(--background)"
                fillOpacity={1}
                isAnimationActive={!reduced}
                animationDuration={800}
                animationEasing="ease-out"
              />
            </>
          ) : null}

          {actualKey && (
            <Line
              type="monotone"
              dataKey={actualKey}
              stroke="var(--muted-foreground)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={!reduced}
              animationDuration={1000}
              animationEasing="ease-out"
              name="Actual"
            />
          )}
          <Line
            type="monotone"
            dataKey={predictedKey}
            stroke="var(--violet)"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2, stroke: "var(--violet)", fill: "var(--background)" }}
            isAnimationActive={!reduced}
            animationDuration={800}
            animationEasing="ease-out"
            name="Predicted"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
