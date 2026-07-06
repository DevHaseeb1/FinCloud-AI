"use client";

export function ChartTooltip({
  active,
  payload,
  label,
  valueFormatter,
  labelFormatter,
}: {
  active?: boolean;
  payload?: Array<{
    value: number;
    name?: string;
    dataKey?: string;
    color?: string;
    stroke?: string;
  }>;
  label?: string;
  valueFormatter?: (value: number) => string;
  labelFormatter?: (label: string) => string;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-xl border border-white/10 bg-popover px-3.5 py-2.5 shadow-xl">
      {label && (
        <div className="mb-1.5 text-[11px] font-medium text-muted-foreground">
          {labelFormatter ? labelFormatter(label) : label}
        </div>
      )}
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <span
            className="size-2 rounded-full"
            style={{ backgroundColor: entry.color || entry.stroke }}
          />
          <span className="text-muted-foreground">{entry.name || entry.dataKey}:</span>
          <span className="font-mono font-semibold text-foreground">
            {valueFormatter
              ? valueFormatter(typeof entry.value === "number" ? entry.value : Number(entry.value))
              : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}
