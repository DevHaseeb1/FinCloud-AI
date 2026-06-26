"use client";

import * as React from "react";
import { Box, Component, Code2, Database, Brain, Route, Radio } from "lucide-react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";

const STATS = [
  { icon: Box, value: "30+", label: "Backend Modules" },
  { icon: Component, value: "40+", label: "React Components" },
  { icon: Code2, value: "5000+", label: "Lines of Code" },
  { icon: Database, value: "8", label: "Database Tables" },
  { icon: Brain, value: "3", label: "ML Models" },
  { icon: Route, value: "30", label: "REST APIs" },
  { icon: Radio, value: "Real-Time", label: "Streaming Pipeline" },
];

function StatCard({
  stat,
  index,
  reduced,
}: {
  stat: (typeof STATS)[number];
  index: number;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (reduced) { setVisible(true); return; }
    const t = setTimeout(() => setVisible(true), staggerDelay(index, 80));
    return () => clearTimeout(t);
  }, [index, reduced]);

  return (
    <div
      className={cn(
        "flex flex-col items-center rounded-xl border border-white/[0.06] bg-[#0D1225] p-6 transition-all duration-400 hover:border-white/[0.12] hover:shadow-[0_0_24px_rgba(0,212,255,0.04)]",
        !visible && "opacity-0 translate-y-3",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="mb-3 flex size-10 items-center justify-center rounded-lg bg-cyan/10">
        <stat.icon className="size-5 text-cyan" />
      </div>
      <span className="text-xl font-bold text-white md:text-2xl">{stat.value}</span>
      <span className="mt-1 text-xs text-white/50 text-center">{stat.label}</span>
    </div>
  );
}

export function TechExcellenceSection() {
  const reduced = useReducedMotion();

  return (
    <section className="bg-[#0A0E1A] py-20 md:py-28">
      <div className="mx-auto max-w-5xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">Technical Excellence</h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            Built with modern technologies and production-grade engineering.
          </p>
        </div>
        <div className="mt-12 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-7">
          {STATS.map((stat, i) => (
            <StatCard key={stat.label} stat={stat} index={i} reduced={reduced} />
          ))}
        </div>
      </div>
    </section>
  );
}
