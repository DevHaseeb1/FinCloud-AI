"use client";

import * as React from "react";
import { motion, useInView } from "framer-motion";
import { useCountUp, staggerContainer, staggerItem } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";

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
}: {
  value: number;
  prefix?: string;
  suffix: string;
  label: string;
}) {
  const counted = useCountUp(value, 1200);

  return (
    <motion.div variants={staggerItem} className="flex flex-col items-center">
      <span className="text-2xl font-bold text-white md:text-3xl font-mono tracking-tight">
        {value > 0 ? `${prefix ?? ""}${counted}${suffix}` : prefix}
      </span>
      <span className="mt-1 text-xs text-white/50 text-center leading-tight">{label}</span>
    </motion.div>
  );
}

export function StatsBar() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="border-y border-white/[0.06] bg-card">
      <div className="mx-auto max-w-7xl px-6 md:px-20 py-12 md:py-16">
        <motion.div
          ref={ref}
          className="grid grid-cols-2 gap-8 md:grid-cols-3 lg:grid-cols-6"
          variants={staggerContainer}
          initial="hidden"
          animate={reduced || isInView ? "visible" : "hidden"}
        >
          {STATS.map((stat) => (
            <StatItem key={stat.label} {...stat} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
