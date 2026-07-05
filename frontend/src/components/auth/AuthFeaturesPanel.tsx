"use client";

import * as React from "react";
import { Activity, Radar, TrendingUp, Sparkles } from "lucide-react";
import {
  Bar,
  BarChart as RBarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { motion, useInView } from "framer-motion";
import { staggerContainer, staggerItem, fadeUpDelayed } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";

const BAR_DATA = [
  { month: "Jan", cost: 12400 },
  { month: "Feb", cost: 14200 },
  { month: "Mar", cost: 16800 },
  { month: "Apr", cost: 18500 },
  { month: "May", cost: 21300 },
  { month: "Jun", cost: 24100 },
];

const FEATURES = [
  { icon: Activity, title: "Real-Time Monitoring", desc: "Track spend across all services instantly" },
  { icon: Radar, title: "AI Anomaly Detection", desc: "Detect unusual cost spikes automatically" },
  { icon: TrendingUp, title: "Cost Forecasting", desc: "Predict future costs with ML models" },
  { icon: Sparkles, title: "Smart Savings", desc: "Get actionable optimization recommendations" },
] as const;

function AmbientOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      <div
        className="absolute -left-32 -top-32 size-96 rounded-full bg-cyan/10 blur-3xl animate-particle-drift"
        style={{ animationDelay: "0s" }}
      />
      <div
        className="absolute -bottom-32 -right-32 size-96 rounded-full bg-violet/10 blur-3xl animate-particle-drift"
        style={{ animationDelay: "2s" }}
      />
    </div>
  );
}

function CostBarChart({ reduced }: { reduced: boolean }) {
  const formatter = (v: number) =>
    `$${(v / 1000).toFixed(v >= 10000 ? 0 : 1)}k`;

  return (
    <div className="h-36 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RBarChart data={BAR_DATA} margin={{ left: -16, right: 0, top: 4, bottom: 0 }}>
          <XAxis
            dataKey="month"
            tickMargin={4}
            axisLine={false}
            tickLine={false}
            stroke="rgba(255,255,255,0.25)"
            style={{ fontSize: "10px" }}
          />
          <YAxis
            tickFormatter={formatter}
            width={40}
            axisLine={false}
            tickLine={false}
            stroke="rgba(255,255,255,0.25)"
            style={{ fontSize: "10px" }}
          />
          <Tooltip
            formatter={(v: string | number) => [`$${Number(v).toLocaleString()}`, "Cost"]}
            contentStyle={{
              backgroundColor: "var(--surface-raised)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "6px",
              color: "#fff",
              fontSize: "12px",
            }}
            labelStyle={{ color: "rgba(255,255,255,0.6)" }}
          />
          <Bar
            dataKey="cost"
            fill="var(--cyan)"
            radius={[4, 4, 0, 0]}
            isAnimationActive={!reduced}
            animationDuration={600}
            animationEasing="ease-out"
            opacity={0.8}
          />
        </RBarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AuthFeaturesPanel({ variant }: { variant: "signup" | "login" }) {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div className="relative hidden w-1/2 flex-col items-center justify-center bg-background p-12 lg:flex overflow-y-auto">
      <AmbientOrbs />
      <div ref={ref} className="relative z-10 flex w-full max-w-sm flex-col items-center gap-6">
        {/* Brand */}
        <motion.div
          className="flex flex-col items-center"
          initial={reduced ? false : "hidden"}
          animate={reduced || isInView ? "visible" : "hidden"}
          variants={fadeUpDelayed(0)}
        >
          <div className="mb-4 size-12 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 14.5a4 4 0 0 1 2.5-7 5.5 5.5 0 0 1 10.2-1.7A4.5 4.5 0 0 1 18 14.5H6a1 1 0 0 1-1-1z" fill="white" opacity="0.9" />
              <path d="M9 14.5v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3M12 10.5v-3M8 17.5h8M9.5 17.5l-1 3M14.5 17.5l1 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">FinCloud-AI</h1>
          <p className="mt-2 text-sm text-white/60">
            {variant === "signup"
              ? "Start monitoring your cloud spend"
              : "Cloud cost intelligence"}
          </p>
        </motion.div>

        {/* Features or Badges */}
        {variant === "signup" ? (
          <motion.div
            className="grid grid-cols-2 gap-2.5"
            initial={reduced ? false : "hidden"}
            animate={reduced || isInView ? "visible" : "hidden"}
            variants={staggerContainer}
          >
            {FEATURES.map((f) => (
              <motion.div
                key={f.title}
                variants={staggerItem}
                className="rounded-lg border border-white/[0.08] bg-white/[0.04] p-2.5"
              >
                <f.icon className="mb-1.5 size-4 text-cyan" />
                <p className="text-xs font-medium text-white/90">{f.title}</p>
                <p className="mt-0.5 text-[11px] text-white/50 leading-tight">
                  {f.desc}
                </p>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <motion.div
            className="flex flex-wrap justify-center gap-2"
            initial={reduced ? false : "hidden"}
            animate={reduced || isInView ? "visible" : "hidden"}
            variants={staggerContainer}
          >
            {FEATURES.map((f) => (
              <motion.span
                key={f.title}
                variants={staggerItem}
                className="inline-flex items-center gap-1.5 rounded-full border border-white/[0.08] bg-white/[0.04] px-2.5 py-1 text-xs text-white/70"
              >
                <f.icon className="size-3 text-cyan" />
                {f.title.replace("Real-Time ", "").replace("AI ", "").replace("Cost ", "").replace("Smart ", "")}
              </motion.span>
            ))}
          </motion.div>
        )}

        {/* Chart */}
        {variant === "login" && (
          <motion.div
            className="w-full rounded-xl border border-white/[0.08] bg-white/[0.04] p-3.5"
            initial={reduced ? false : "hidden"}
            animate={reduced || isInView ? "visible" : "hidden"}
            variants={fadeUpDelayed(0.3)}
          >
            <p className="mb-2.5 text-[11px] font-medium text-white/40 uppercase tracking-wider">
              Cost trend
            </p>
            <CostBarChart reduced={reduced} />
          </motion.div>
        )}
      </div>
    </div>
  );
}
