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
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "#F97316",
];

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
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RPieChart>
          <Tooltip
            formatter={(v, _n, p) => {
              const num = typeof v === "number" ? v : Number(v);
              return [valueFormatter?.(num) ?? num, p?.payload?.[nameKey] ?? ""];
            }}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "6px",
              color: "hsl(var(--foreground))",
            }}
            labelStyle={{ color: "hsl(var(--foreground))" }}
          />
          <Legend
            verticalAlign="bottom"
            height={24}
            wrapperStyle={{ fontSize: "12px", color: "hsl(var(--foreground))" }}
          />
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            isAnimationActive={!reduced}
            animationDuration={800}
            animationEasing="ease-out"
          >
            {data.map((_d, idx) => (
              <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
        </RPieChart>
      </ResponsiveContainer>
    </div>
  );
}
