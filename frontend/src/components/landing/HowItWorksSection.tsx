"use client";

import * as React from "react";
import { Cloud, Database, Brain, Lightbulb } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { staggerItem, easeOutExpo } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
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

function StepCard({
  step,
  index,
  isInView,
  reduced,
}: {
  step: (typeof STEPS)[number];
  index: number;
  isInView: boolean;
  reduced: boolean;
}) {
  return (
    <motion.div
      initial={reduced ? false : "hidden"}
      animate={reduced || isInView ? "visible" : "hidden"}
      variants={{
        hidden: { opacity: 0, y: 24 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { ...easeOutExpo, delay: index * 0.12 },
        },
      }}
      className="relative flex flex-col items-center text-center"
    >
      <div className={cn("relative z-10 flex size-12 items-center justify-center rounded-xl bg-gradient-to-br", step.gradient)}>
        <step.icon className="size-6 text-white" />
      </div>
      <div className="mt-3 rounded-full border border-white/[0.06] bg-background px-2.5 py-0.5 text-xs text-white/40 font-mono">
        Step {index + 1}
      </div>
      <h3 className="mt-2 text-base font-semibold text-white">{step.title}</h3>
      <p className="mt-1.5 text-sm text-white/50 leading-relaxed">{step.description}</p>
    </motion.div>
  );
}

export function HowItWorksSection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="how-it-works" className="bg-card py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-6 md:px-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">How FinCloud-AI Works</h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            From AWS connection to actionable insights in four steps.
          </p>
        </div>

        <div ref={ref} className="mt-10 grid grid-cols-1 gap-8 md:grid-cols-4 md:gap-6 relative">
          {/* Connector line */}
          <div className="absolute left-0 right-0 top-6 hidden h-px bg-gradient-to-r from-cyan via-violet to-ember md:block" />

          {STEPS.map((step, i) => (
            <StepCard
              key={step.title}
              step={step}
              index={i}
              isInView={isInView}
              reduced={reduced}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
