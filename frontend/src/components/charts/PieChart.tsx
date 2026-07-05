"use client";

import {
  Pie,
  PieChart as RPieChart,
  ResponsiveContainer,
  Tooltip,
  Cell,
  Legend,
} from "recharts";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const COLORS = [
  "var(--cyan)",
  "var(--violet)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--ember)",
];

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const data = payload[0];
  return (
    <div className="rounded-xl border border-white/10 bg-popover px-3.5 py-2.5 shadow-xl">
      <div className="flex items-center gap-2 text-sm">
        <span
          className="size-2 rounded-full"
          style={{ backgroundColor: data.payload?.fill || data.color }}
        />
        <span className="text-muted-foreground">{data.name}:</span>
        <span className="font-mono font-semibold text-foreground">{data.value}</span>
      </div>
    </div>
  );
}

function CustomLegend({ payload }: any) {
  if (!payload) return null;
  return (
    <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 pt-2">
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span
            className="size-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span>{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

function renderCustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) {
  if (percent < 0.05) return null;
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontWeight={600}
      fontFamily="var(--font-mono)"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

export function PieChart({
  data,
  nameKey,
  valueKey,
  valueFormatter,
}: {
  data: Array<Record<string, any>>;
  nameKey: string;
  valueKey: string;
  valueFormatter?: (v: number) => string;
}) {
  const reduced = useReducedMotion();

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RPieChart>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
            label={renderCustomLabel}
            labelLine={false}
            isAnimationActive={!reduced}
            animationDuration={800}
            animationEasing="ease-out"
          >
            {data.map((_d, idx) => (
              <Cell
                key={idx}
                fill={COLORS[idx % COLORS.length]}
                stroke="var(--background)"
                strokeWidth={2}
              />
            ))}
          </Pie>
        </RPieChart>
      </ResponsiveContainer>
    </div>
  );
}
