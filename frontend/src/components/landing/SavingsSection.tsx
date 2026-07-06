"use client";

import * as React from "react";
import { TrendingUp, Shield, BadgeCheck } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, staggerItem, springTransition } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";
import { formatCurrency } from "@/lib/format";

const RECOMMENDATIONS = [
  {
    priority: "high",
    title: "EC2 Rightsizing",
    description: "Downsize m5.xlarge to m5.large instances in production. Current utilization averages 18% over 30 days.",
    savings: 4200,
    confidence: 94,
    icon: TrendingUp,
  },
  {
    priority: "medium",
    title: "Reserved Instances",
    description: "Purchase 1-year Standard RI for consistent EC2 workloads in us-east-1. Break-even in 4 months.",
    savings: 2100,
    confidence: 88,
    icon: Shield,
  },
  {
    priority: "low",
    title: "S3 Storage Optimization",
    description: "Transition 340GB of infrequently accessed data from S3 Standard to S3 Glacier Instant Retrieval.",
    savings: 840,
    confidence: 82,
    icon: BadgeCheck,
  },
];

function RecCard({
  rec,
}: {
  rec: (typeof RECOMMENDATIONS)[number];
}) {
  const priorityColor =
    rec.priority === "high"
      ? "bg-ember/10 text-ember border-ember/20"
      : rec.priority === "medium"
        ? "bg-violet/10 text-violet border-violet/20"
        : "bg-cyan/10 text-cyan border-cyan/20";

  return (
    <motion.div
      variants={staggerItem}
      whileHover={{ y: -4, transition: springTransition }}
      className="rounded-xl border border-white/[0.06] bg-card p-5 transition-shadow duration-400 hover:border-white/[0.12]"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex size-10 items-center justify-center rounded-lg bg-cyan/10">
            <rec.icon className="size-5 text-cyan" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">{rec.title}</h3>
            <p className="mt-1 text-sm text-white/60 leading-relaxed">{rec.description}</p>
          </div>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase", priorityColor)}>
          {rec.priority} priority
        </span>
        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-0.5 text-xs text-emerald-400 font-medium">
          <TrendingUp className="size-3" />
          {formatCurrency(rec.savings)}/mo
        </span>
        <span className="text-xs text-white/40 font-mono">
          {rec.confidence}% confidence
        </span>
      </div>
    </motion.div>
  );
}

export function SavingsSection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="savings" className="bg-card py-16 md:py-24">
      <div className="mx-auto max-w-5xl px-6 md:px-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">
            AI-Generated Recommendations
          </h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            Machine learning identifies cost-saving opportunities across your AWS environment with estimated dollar impact.
          </p>
        </div>
        <div ref={ref} className="mt-10 space-y-3">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate={reduced || isInView ? "visible" : "hidden"}
            className="space-y-3"
          >
            {RECOMMENDATIONS.map((rec) => (
              <RecCard key={rec.title} rec={rec} />
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
