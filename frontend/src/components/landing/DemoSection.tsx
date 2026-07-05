"use client";

import * as React from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { Lightbulb, TrendingUp } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { fadeUpDelayed } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const DATA = [
  { day: "Day 1", cost: 3000 },
  { day: "Day 5", cost: 3800 },
  { day: "Day 10", cost: 4500 },
  { day: "Day 15", cost: 5200 },
  { day: "Day 20", cost: 5500 },
  { day: "Day 25", cost: 5800 },
  { day: "Day 30", cost: 6000 },
];

const formatter = (v: number) => `$${(v / 1000).toFixed(1)}K`;

export function DemoSection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="demo" className="bg-background py-16 md:py-24">
      <div className="mx-auto max-w-7xl px-6 md:px-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">
            Cloud Cost Forecast
          </h2>
          <p className="mt-3 text-white/50 max-w-xl mx-auto">
            30-day cloud spend forecast. Sample AWS cost forecast generated using Prophet.
          </p>
        </div>

        <div ref={ref} className="mt-12 grid gap-10 lg:grid-cols-3">
          {/* Chart */}
          <motion.div
            className="lg:col-span-2 rounded-xl border border-white/[0.08] bg-card p-5 md:p-6"
            initial={reduced ? false : "hidden"}
            animate={reduced || isInView ? "visible" : "hidden"}
            variants={fadeUpDelayed(0.1)}
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="size-4 text-cyan" />
              <span className="text-sm font-medium text-white/80">30-Day Spend Forecast</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={DATA} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="demoGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--cyan)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="var(--cyan)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} stroke="rgba(255,255,255,0.1)" />
                  <XAxis
                    dataKey="day"
                    tickMargin={8}
                    axisLine={false}
                    tickLine={false}
                    stroke="rgba(255,255,255,0.25)"
                    style={{ fontSize: "12px" }}
                  />
                  <YAxis
                    tickFormatter={formatter}
                    width={50}
                    axisLine={false}
                    tickLine={false}
                    stroke="rgba(255,255,255,0.25)"
                    style={{ fontSize: "12px" }}
                  />
                  <Tooltip
                    formatter={(v: string | number) => [`$${Number(v).toLocaleString()}`, "Projected Cost"]}
                    contentStyle={{
                      backgroundColor: "var(--surface-raised)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: "6px",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                    labelStyle={{ color: "rgba(255,255,255,0.6)" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="cost"
                    stroke="var(--cyan)"
                    strokeWidth={2}
                    fill="url(#demoGradient)"
                    isAnimationActive={!reduced}
                    animationDuration={1000}
                    animationEasing="ease-out"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* AI Insight panel */}
          <motion.div
            className="rounded-xl border border-violet/20 bg-violet/[0.04] p-6 flex flex-col justify-center"
            initial={reduced ? false : "hidden"}
            animate={reduced || isInView ? "visible" : "hidden"}
            variants={fadeUpDelayed(0.2)}
          >
            <div className="mb-3 flex size-10 items-center justify-center rounded-lg bg-violet/20">
              <Lightbulb className="size-5 text-violet" />
            </div>
            <h3 className="text-lg font-semibold text-white">AI Insight</h3>
            <p className="mt-2 text-sm text-white/70 leading-relaxed">
              Forecast indicates a <span className="text-ember font-medium">17% increase</span>{" "}
              in monthly AWS spending.
            </p>
            <div className="mt-4 rounded-lg border border-white/[0.06] bg-white/[0.03] p-3">
              <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Primary Driver</p>
              <p className="mt-1 text-sm text-white/90 font-medium">EC2 Compute Usage</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="h-1.5 flex-1 rounded-full bg-white/[0.06] overflow-hidden">
                  <div className="h-full w-3/4 rounded-full bg-cyan" />
                </div>
                <span className="text-xs text-white/50 font-mono">74%</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
