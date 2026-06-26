"use client";

import * as React from "react";
import { Cloud, Database, Brain, BarChart3, LayoutDashboard, MessageSquareText, Bell, ArrowRight, ArrowDown } from "lucide-react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

const STAGES = [
  {
    title: "Data Sources",
    color: "cyan",
    items: [
      { label: "AWS Cost Explorer", result: null },
      { label: "Data Pipeline", result: null },
      { label: "Feature Engineering", result: null },
    ],
  },
  {
    title: "AI Engine",
    color: "violet",
    items: [
      { label: "Isolation Forest", result: "Anomaly Detection" },
      { label: "Prophet", result: "Forecast" },
      { label: "Random Forest", result: "Savings" },
    ],
  },
  {
    title: "Outputs",
    color: "emerald",
    items: [
      { label: "Dashboard", result: null },
      { label: "Slack", result: null },
      { label: "PagerDuty", result: null },
    ],
  },
];

const colorMap = {
  cyan: { dot: "bg-cyan", border: "border-cyan/20", text: "text-cyan", bg: "bg-cyan/[0.04]" },
  violet: { dot: "bg-violet", border: "border-violet/20", text: "text-violet", bg: "bg-violet/[0.04]" },
  emerald: { dot: "bg-emerald-400", border: "border-emerald-400/20", text: "text-emerald-400", bg: "bg-emerald-400/[0.04]" },
};

const resultColorMap: Record<string, string> = {
  "Anomaly Detection": "bg-cyan/10 text-cyan",
  Forecast: "bg-violet/10 text-violet",
  Savings: "bg-emerald-400/10 text-emerald-400",
};

function StageCard({
  stage,
  delay,
  reduced,
}: {
  stage: (typeof STAGES)[number];
  delay: number;
  reduced: boolean;
}) {
  const c = colorMap[stage.color as keyof typeof colorMap];

  return (
    <div
      className={cn(
        "flex-1 rounded-xl border bg-[#0D1225]/60 p-3 transition-all duration-500 hover:border-white/[0.12]",
        c.border,
        reduced ? "" : "opacity-0 translate-y-3",
      )}
      style={{
        animation: reduced ? "none" : `fade-up 400ms var(--ease-out-expo) ${delay}ms forwards`,
      }}
    >
      <div className={cn("text-[11px] font-semibold uppercase tracking-wider mb-2", c.text)}>
        {stage.title}
      </div>
      <div className="space-y-1.5">
        {stage.items.map((item, i) => (
          <div key={i} className="flex items-center gap-2 text-sm flex-wrap">
            <span className={cn("size-1.5 shrink-0 rounded-full", c.dot)} />
            <span className="text-white/80">{item.label}</span>
            {item.result && (
              <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium", resultColorMap[item.result])}>
                {item.result}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function ArchitectureSection() {
  const reduced = useReducedMotion();

  return (
    <section id="architecture" className="relative bg-[#0A0E1A] py-12 md:py-16 overflow-hidden">
      <div className="absolute left-1/2 top-1/2 size-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan/[0.02] blur-3xl" />

      <div className="relative z-10 mx-auto max-w-5xl px-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white md:text-3xl">Architecture</h2>
          <p className="mt-2 text-sm text-white/50 max-w-xl mx-auto">
            End-to-end ML pipeline for real-time cloud cost intelligence.
          </p>
        </div>

        <div
          className={cn(
            "mt-8 rounded-2xl border border-white/[0.06] bg-[#0D1225]/80 p-4 backdrop-blur-sm md:p-6",
            reduced ? "" : "opacity-0",
          )}
          style={{
            animation: reduced ? "none" : "fade-up 500ms var(--ease-out-expo) 100ms forwards",
          }}
        >
          <div className="flex flex-col gap-3 lg:flex-row lg:items-stretch lg:gap-2">
            {STAGES.map((stage, i) => (
              <React.Fragment key={stage.title}>
                <StageCard stage={stage} delay={200 + i * 200} reduced={reduced} />
                {i < STAGES.length - 1 && (
                  <div className="flex items-center justify-center py-1 lg:py-0">
                    <ArrowRight className="size-4 text-white/20 hidden lg:block" />
                    <ArrowDown className="size-4 text-white/20 lg:hidden" />
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
