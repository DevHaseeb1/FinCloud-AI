"use client";

import * as React from "react";
import { Radar, TrendingUp, Sparkles, Globe, Activity, Bell } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { staggerContainer, staggerItem, springTransition } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

const FEATURES = [
  {
    icon: Radar,
    title: "AI Anomaly Detection",
    description: "Isolation Forest with 28 engineered features, severity scoring, and human-readable explanations for every anomaly.",
    gradient: "from-cyan to-blue-500",
  },
  {
    icon: TrendingUp,
    title: "Cost Forecasting",
    description: "30-day prediction with confidence intervals, service-level forecasting, and trend visualization powered by Prophet.",
    gradient: "from-violet to-purple-500",
  },
  {
    icon: Sparkles,
    title: "Optimization Recommendations",
    description: "Right-sizing opportunities, reserved instance suggestions, consolidation opportunities, and estimated dollar savings.",
    gradient: "from-emerald-400 to-teal-500",
  },
  {
    icon: Globe,
    title: "AWS Multi-Account Integration",
    description: "CloudFormation setup, STS AssumeRole, External IDs, and encrypted credential storage for secure cross-account access.",
    gradient: "from-ember to-orange-500",
  },
  {
    icon: Activity,
    title: "Real-Time Monitoring",
    description: "Kinesis streaming, continuous processing, and instant anomaly detection for your entire AWS environment.",
    gradient: "from-pink-500 to-rose-500",
  },
  {
    icon: Bell,
    title: "Alerting & Notifications",
    description: "Slack alerts, PagerDuty integration, severity mapping, and incident escalation to keep your team informed.",
    gradient: "from-cyan to-violet",
  },
];

function FeatureCard({
  item,
}: {
  item: (typeof FEATURES)[number];
}) {
  return (
    <motion.div
      variants={staggerItem}
      whileHover={{ y: -4, transition: springTransition }}
      className="group relative overflow-hidden rounded-xl border border-white/[0.06] bg-card p-5 transition-shadow duration-400 hover:border-white/[0.12] hover:shadow-[0_0_24px] hover:shadow-primary/6"
    >
      <div
        className="absolute inset-[-1px] rounded-[11px] pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-400"
        style={{
          background: "conic-gradient(from var(--border-angle, 0deg), var(--cyan) 0%, var(--violet) 40%, var(--cyan) 80%, transparent 100%)",
          WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          WebkitMaskComposite: "xor",
          mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          maskComposite: "exclude",
          padding: "1px",
          animation: "gradient-border-spin 3s linear infinite",
        }}
      />
      <div className={cn("mb-3 flex size-10 items-center justify-center rounded-lg bg-gradient-to-br", item.gradient)}>
        <item.icon className="size-5 text-white" />
      </div>
      <h3 className="text-base font-semibold text-white">{item.title}</h3>
      <p className="mt-1.5 text-sm text-white/60 leading-relaxed">{item.description}</p>
    </motion.div>
  );
}

export function FeaturesSection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" className="bg-background py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-6 md:px-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">
            Core Platform Features
          </h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            Everything you need to monitor, forecast, and optimize your cloud spending.
          </p>
        </div>
        <div ref={ref} className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <motion.div
            className="contents"
            variants={staggerContainer}
            initial="hidden"
            animate={reduced || isInView ? "visible" : "hidden"}
          >
            {FEATURES.map((item) => (
              <FeatureCard key={item.title} item={item} />
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
