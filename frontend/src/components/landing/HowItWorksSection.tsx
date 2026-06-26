"use client";

import * as React from "react";
import { Cloud, Database, Brain, Lightbulb } from "lucide-react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";

const STEPS = [
  {
    icon: Cloud,
    title: "Connect AWS Account",
    description: "CloudFormation generates a secure cross-account IAM role in minutes.",
    gradient: "from-cyan to-blue-500",
  },
  {
    icon: Database,
    title: "Collect Cost Data",
    description: "AWS Cost Explorer and CUR data ingestion with automatic ETL processing.",
    gradient: "from-violet to-purple-500",
  },
  {
    icon: Brain,
    title: "AI Processing",
    description: "Feature engineering, anomaly detection, forecasting, and optimization in a single pipeline.",
    gradient: "from-emerald-400 to-teal-500",
  },
  {
    icon: Lightbulb,
    title: "Actionable Insights",
    description: "Recommendations, alerts, and savings opportunities delivered to your dashboard and integrations.",
    gradient: "from-ember to-orange-500",
  },
];

export function HowItWorksSection() {
  const reduced = useReducedMotion();

  return (
    <section id="how-it-works" className="bg-[#0D1225] py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">How FinCloud-AI Works</h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            From AWS connection to actionable insights in four steps.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-4 relative">
          {/* Connector line */}
          <div className="absolute left-0 top-12 hidden h-px w-full bg-gradient-to-r from-cyan via-violet to-ember md:block" />

          {STEPS.map((step, i) => (
            <StepCard key={step.title} step={step} index={i} reduced={reduced} isLast={i === STEPS.length - 1} />
          ))}
        </div>
      </div>
    </section>
  );
}

function StepCard({
  step,
  index,
  reduced,
  isLast,
}: {
  step: (typeof STEPS)[number];
  index: number;
  reduced: boolean;
  isLast: boolean;
}) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (reduced) { setVisible(true); return; }
    const t = setTimeout(() => setVisible(true), staggerDelay(index, 150));
    return () => clearTimeout(t);
  }, [index, reduced]);

  return (
    <div
      className={cn(
        "relative flex flex-col items-center text-center transition-all duration-500",
        !visible && "opacity-0 translate-y-6",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className={cn("relative z-10 flex size-12 items-center justify-center rounded-xl bg-gradient-to-br", step.gradient)}>
        <step.icon className="size-6 text-white" />
      </div>
      <div className="mt-3 rounded-full border border-white/[0.06] bg-[#0A0E1A] px-2.5 py-0.5 text-xs text-white/40 font-mono">
        Step {index + 1}
      </div>
      <h3 className="mt-2 text-base font-semibold text-white">{step.title}</h3>
      <p className="mt-1.5 text-sm text-white/50 leading-relaxed">{step.description}</p>
    </div>
  );
}
