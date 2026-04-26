"use client";

import {
  Pie,
  PieChart as RPieChart,
  ResponsiveContainer,
  Tooltip,
  Cell,
  Legend,
} from "recharts";

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
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
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RPieChart>
          <Tooltip
            formatter={(v, _n, p) => {
              const num = typeof v === "number" ? v : Number(v);
              return [valueFormatter?.(num) ?? num, p?.payload?.[nameKey] ?? ""];
            }}
          />
          <Legend verticalAlign="bottom" height={24} />
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
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

