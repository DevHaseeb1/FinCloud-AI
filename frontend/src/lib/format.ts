export function formatCurrency(
  value: number | undefined | null,
  opts?: { currency?: string },
) {
  const n = typeof value === "number" ? value : 0;
  const currency = opts?.currency || "USD";
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(n);
}

export function formatPct(value: number | undefined | null) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
}

