"use client";

import * as React from "react";
import { useCountUp, staggerDelay } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

const STATS = [
  { value: 30, suffix: "+", label: "API Endpoints" },
  { value: 3, suffix: "", label: "ML Models" },
  { value: 28, suffix: "", label: "Engineered Features" },
  { value: 95, suffix: "%", label: "Forecast Confidence" },
  { value: 0, prefix: "Real-Time ", suffix: "", label: "AWS Monitoring" },
  { value: 18, prefix: "$", suffix: "K+", label: "Potential Savings" },
];

function StatItem({
  value,
  prefix,
  suffix,
  label,
  index,
  reduced,
}: {
  value: number;
  prefix?: string;
  suffix: string;
  label: string;
  index: number;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);
  const counted = useCountUp(value, 1200, reduced);

  React.useEffect(() => {
    if (reduced) { setVisible(true); return; }
    const t = setTimeout(() => setVisible(true), staggerDelay(index, 100));
    return () => clearTimeout(t);
  }, [index, reduced]);

  return (
    <div
      className={cn(
        "flex flex-col items-center transition-all duration-500",
        !visible && "opacity-0 translate-y-4",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <span className="text-2xl font-bold text-white md:text-3xl font-mono tracking-tight">
        {value > 0 ? `${prefix ?? ""}${counted}${suffix}` : prefix}
      </span>
      <span className="mt-1 text-xs text-white/50 text-center leading-tight">{label}</span>
    </div>
  );
}

export function StatsBar() {
  const reduced = useReducedMotion();

  return (
    <section className="border-y border-white/[0.06] bg-[#0D1225]">
      <div className="mx-auto max-w-7xl px-6 py-12 md:py-16">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-3 lg:grid-cols-6">
          {STATS.map((stat, i) => (
            <StatItem key={stat.label} {...stat} index={i} reduced={reduced} />
          ))}
        </div>
      </div>
    </section>
  );
}
