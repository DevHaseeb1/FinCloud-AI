"use client";

import * as React from "react";
import { Shield, TrendingUp, Sparkles } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, staggerItem, springTransition } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

const MODELS = [
  {
    icon: Shield,
    name: "Anomaly Detection",
    model: "Isolation Forest",
    description: "Flags unusual spending patterns by learning the normal behavior of each account, service, and region. Detects spikes, drifts, and outliers before they become expensive problems.",
    color: "cyan",
    gradient: "from-cyan to-blue-500",
    example: "EC2 us-east-1 cost 3.2x above 30-day average",
  },
  {
    icon: TrendingUp,
    name: "Cost Forecasting",
    model: "Facebook Prophet",
    description: "Predicts future cloud spend 30 days ahead with confidence intervals. Accounts for seasonality, trends, and growth patterns to give you an accurate picture of where your budget is heading.",
    color: "violet",
    gradient: "from-violet to-purple-500",
    example: "Monthly spend projected at $114K — 17% increase",
  },
  {
    icon: Sparkles,
    name: "Savings Recommendations",
    model: "Random Forest",
    description: "Prioritizes optimization opportunities by estimating dollar savings and confidence levels. Rightsizing, reserved instances, and storage tiering recommendations ranked by impact.",
    color: "emerald",
    gradient: "from-emerald-400 to-teal-500",
    example: "Right-size m5.xlarge to m5.large — save $4,200/mo",
  },
];

const colorClasses = {
  cyan: { icon: "text-cyan", bg: "bg-cyan/10", border: "border-cyan/20", dot: "bg-cyan" },
  violet: { icon: "text-violet", bg: "bg-violet/10", border: "border-violet/20", dot: "bg-violet" },
  emerald: { icon: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/20", dot: "bg-emerald-400" },
};

function ModelCard({
  model,
}: {
  model: (typeof MODELS)[number];
}) {
  const c = colorClasses[model.color as keyof typeof colorClasses];

  return (
    <motion.div
      variants={staggerItem}
      whileHover={{ y: -4, transition: springTransition }}
      className={cn(
        "rounded-xl border bg-card p-6 transition-shadow duration-400 hover:shadow-[0_0_24px] hover:shadow-primary/6",
        "border-white/[0.06] hover:border-white/[0.12]",
      )}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={cn("flex size-10 items-center justify-center rounded-lg", c.bg)}>
          <model.icon className={cn("size-5", c.icon)} />
        </div>
        <div>
          <p className="text-xs text-white/40 uppercase tracking-wider font-medium">{model.model}</p>
          <h3 className="text-base font-semibold text-white">{model.name}</h3>
        </div>
      </div>
      <p className="text-sm text-white/60 leading-relaxed">{model.description}</p>
      <div className={cn("mt-4 rounded-lg border p-3", c.border, "bg-white/[0.02]")}>
        <p className="text-[11px] text-white/40 uppercase tracking-wider font-medium">Example Output</p>
        <p className={cn("mt-1 text-sm font-medium", c.icon)}>{model.example}</p>
      </div>
    </motion.div>
  );
}

export function HowAIWorksSection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="bg-card py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-6 md:px-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">How the AI Works</h2>
          <p className="mt-3 text-white/50 max-w-2xl mx-auto">
            Three specialized machine learning models work together in a single pipeline to give you complete cloud cost intelligence.
          </p>
        </div>

        <div ref={ref} className="mt-10 grid gap-6 md:grid-cols-3">
          <motion.div
            className="contents"
            variants={staggerContainer}
            initial="hidden"
            animate={reduced || isInView ? "visible" : "hidden"}
          >
            {MODELS.map((model) => (
              <ModelCard key={model.name} model={model} />
            ))}
          </motion.div>
        </div>

        {/* Pipeline flow */}
        <motion.div
          className="mt-10 flex items-center justify-center gap-3"
          initial={reduced ? false : { opacity: 0 }}
          animate={reduced || isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          {MODELS.map((model, i) => (
            <React.Fragment key={model.name}>
              <div className={cn("size-2 rounded-full", colorClasses[model.color as keyof typeof colorClasses].dot)} />
              {i < MODELS.length - 1 && (
                <div className="h-px w-12 bg-gradient-to-r from-white/20 to-white/10" />
              )}
            </React.Fragment>
          ))}
        </motion.div>
        <motion.p
          className="mt-3 text-center text-xs text-white/40"
          initial={reduced ? false : { opacity: 0 }}
          animate={reduced || isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          Anomaly Detection {"\u2192"} Cost Forecasting {"\u2192"} Savings Recommendations
        </motion.p>
      </div>
    </section>
  );
}
