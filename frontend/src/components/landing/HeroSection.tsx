"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, TrendingUp, AlertTriangle, Wallet, Zap, Activity } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useCountUp, fadeUpDelayed, staggerContainer, staggerItem } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

const bars = [35, 50, 42, 65, 55, 70, 60, 80, 68, 78, 88, 75];

function AmbientOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      <div className="absolute -left-32 -top-32 size-96 rounded-full bg-cyan/[0.08] blur-3xl animate-particle-drift" style={{ animationDelay: "0s" }} />
      <div className="absolute -bottom-32 -right-32 size-96 rounded-full bg-violet/[0.08] blur-3xl animate-particle-drift" style={{ animationDelay: "2s" }} />
      <div className="absolute left-1/3 top-1/2 size-64 rounded-full bg-ember/[0.04] blur-3xl animate-particle-drift" style={{ animationDelay: "4s" }} />
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
}) {
  const counted = useCountUp(value, 1000);

  return (
    <motion.div
      variants={staggerItem}
      className="rounded-lg border border-white/[0.08] bg-white/[0.04] p-3"
    >
      <div className="flex items-center gap-2">
        <span className={cn("size-3.5", color)}>{icon}</span>
        <span className="text-[11px] text-white/50">{label}</span>
      </div>
      <p className="mt-1 text-lg font-bold text-white font-mono tracking-tight">
        {counted.toLocaleString()}
      </p>
    </motion.div>
  );
}

function HeroDashboard({ reduced }: { reduced: boolean }) {
  return (
    <div className="relative rounded-xl border border-white/[0.1] bg-card shadow-[0_0_48px] shadow-primary/8 overflow-hidden">
      {/* Window chrome */}
      <div className="flex items-center gap-1.5 border-b border-white/[0.06] px-4 py-2.5">
        <div className="size-2 rounded-full bg-ember/60" />
        <div className="size-2 rounded-full bg-yellow-500/60" />
        <div className="size-2 rounded-full bg-green-500/60" />
        <span className="ml-2 text-[11px] text-white/30 font-mono">FinCloud Dashboard</span>
      </div>

      <div className="p-3 space-y-2.5">
        {/* Stat cards row */}
        <motion.div
          className="grid grid-cols-2 gap-1.5"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          <StatCard
            icon={<Wallet className="size-3.5" />}
            label="Today's Spend"
            value={3842}
            color="text-cyan"
          />
          <StatCard
            icon={<TrendingUp className="size-3.5" />}
            label="Predicted Month"
            value={114320}
            color="text-violet"
          />
          <StatCard
            icon={<Zap className="size-3.5" />}
            label="Potential Savings"
            value={18750}
            color="text-emerald-400"
          />
          <StatCard
            icon={<Activity className="size-3.5" />}
            label="Active Anomalies"
            value={4}
            color="text-ember"
          />
        </motion.div>

        {/* Mini bar chart */}
        <motion.div
          variants={fadeUpDelayed(0.6)}
          initial="hidden"
          animate="visible"
          className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-2.5"
        >
          <p className="mb-1.5 text-[11px] text-white/40 font-mono">Daily cost trend (past 12 days)</p>
          <div className="flex items-end gap-1 h-16">
            {bars.map((h, i) => (
              <motion.div
                key={i}
                className="flex-1 rounded-t-sm bg-gradient-to-t from-cyan/60 to-cyan/30"
                initial={{ height: 0 }}
                animate={{ height: `${h}%` }}
                transition={{ duration: 0.4, delay: 0.7 + i * 0.04, ease: [0.16, 1, 0.3, 1] }}
              />
            ))}
          </div>
        </motion.div>

        {/* Anomaly alert */}
        <motion.div
          variants={fadeUpDelayed(1.8)}
          initial="hidden"
          animate="visible"
          className="rounded-lg border border-ember/20 bg-ember/[0.06] p-3"
        >
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="size-4 text-ember mt-0.5 shrink-0 animate-anomaly-pulse" />
            <div className="min-w-0">
              <p className="text-xs font-medium text-white/90">Anomaly Detected</p>
              <p className="mt-0.5 text-[11px] text-white/50 truncate">
                EC2 us-east-1 cost spike — 3.2x above normal
              </p>
            </div>
          </div>
        </motion.div>

        {/* Savings recommendation */}
        <motion.div
          variants={fadeUpDelayed(2.4)}
          initial="hidden"
          animate="visible"
          className="rounded-lg border border-cyan/20 bg-cyan/[0.04] p-3"
        >
          <div className="flex items-start gap-2.5">
            <Zap className="size-4 text-cyan mt-0.5 shrink-0" />
            <div className="min-w-0">
              <p className="text-xs font-medium text-white/90">Savings Opportunity</p>
              <p className="mt-0.5 text-[11px] text-white/50 truncate">
                Right-size RDS instances — save ~$1,420/mo
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export function HeroSection() {
  const reduced = useReducedMotion();

  const scrollToDemo = () => {
    const el = document.querySelector("#demo");
    el?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative min-h-[100dvh] flex items-center bg-background overflow-hidden pt-14">
      <AmbientOrbs />
      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 md:px-20 py-8 md:py-16">
        <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
          {/* Left: text */}
          <motion.div
            className="max-w-xl"
            initial={reduced ? false : "hidden"}
            animate="visible"
            variants={fadeUpDelayed(0.1)}
          >
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan/20 bg-cyan/[0.04] px-3 py-1">
              <span className="size-1.5 rounded-full bg-cyan animate-pulse" />
              <span className="text-xs text-cyan font-medium">AI-Powered Cloud Intelligence</span>
            </div>
            <h1 className="text-4xl font-bold leading-[1.1] text-white md:text-5xl lg:text-6xl">
              Stop Cloud Cost Waste{" "}
              <span className="bg-gradient-to-r from-cyan to-violet bg-clip-text text-transparent">
                Before It Happens
              </span>
            </h1>
            <p className="mt-3 text-base leading-relaxed text-white/60 md:text-lg">
              FinCloud-AI uses machine learning to detect billing anomalies, forecast future cloud spend, and generate optimization recommendations across your AWS environment in real time.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Button
                size="lg"
                className="bg-cyan text-space font-semibold hover:brightness-110 text-base px-8 h-12 hover:scale-[1.02] active:scale-[0.98] transition-transform"
                render={<Link href="/signup" />}
                nativeButton={false}
              >
                Get Started
                <ArrowRight className="ml-2 size-4" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white/10 text-white/80 hover:text-white hover:bg-white/[0.06] text-base px-8 h-12 hover:scale-[1.02] active:scale-[0.98] transition-transform"
                onClick={scrollToDemo}
              >
                Live Demo
              </Button>
            </div>
          </motion.div>

          {/* Right: dashboard mockup */}
          <motion.div
            className="w-full max-w-lg mx-auto lg:mx-0 lg:max-w-none"
            initial={reduced ? false : "hidden"}
            animate="visible"
            variants={fadeUpDelayed(0.2)}
          >
            <HeroDashboard reduced={reduced} />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
