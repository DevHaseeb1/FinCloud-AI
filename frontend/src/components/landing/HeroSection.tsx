"use client";

import * as React from "react";
import { ArrowRight, TrendingUp, AlertTriangle, Wallet, Zap, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCountUp, staggerDelay } from "@/lib/animations";
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
  index,
  reduced,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
  index: number;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);
  const counted = useCountUp(value, 1000, reduced);

  React.useEffect(() => {
    const t = setTimeout(() => setVisible(true), staggerDelay(index, 120));
    return () => clearTimeout(t);
  }, [index]);

  return (
    <div
      className={cn(
        "rounded-lg border border-white/[0.08] bg-white/[0.04] p-3 transition-all duration-400",
        !visible && "opacity-0 translate-y-3",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="flex items-center gap-2">
        <span className={cn("size-3.5", color)}>{icon}</span>
        <span className="text-[11px] text-white/50">{label}</span>
      </div>
      <p className="mt-1 text-lg font-bold text-white font-mono tracking-tight">
        {counted.toLocaleString()}
      </p>
    </div>
  );
}

function HeroDashboard({ reduced }: { reduced: boolean }) {
  const [alertVisible, setAlertVisible] = React.useState(false);

  React.useEffect(() => {
    if (reduced) return;
    const t = setTimeout(() => setAlertVisible(true), 2200);
    return () => clearTimeout(t);
  }, [reduced]);

  const [showRec, setShowRec] = React.useState(false);
  React.useEffect(() => {
    if (reduced) return;
    const t = setTimeout(() => setShowRec(true), 3800);
    return () => clearTimeout(t);
  }, [reduced]);

  return (
    <div className="relative rounded-xl border border-white/[0.1] bg-[#0D1225] shadow-[0_0_48px_rgba(0,212,255,0.08)] overflow-hidden">
      {/* Window chrome */}
      <div className="flex items-center gap-1.5 border-b border-white/[0.06] px-4 py-2.5">
        <div className="size-2 rounded-full bg-ember/60" />
        <div className="size-2 rounded-full bg-yellow-500/60" />
        <div className="size-2 rounded-full bg-green-500/60" />
        <span className="ml-2 text-[11px] text-white/30 font-mono">FinCloud Dashboard</span>
      </div>

      <div className="p-3 space-y-2.5">
        {/* Stat cards row */}
        <div className="grid grid-cols-2 gap-1.5">
          <StatCard
            icon={<Wallet className="size-3.5" />}
            label="Today's Spend"
            value={3842}
            color="text-cyan"
            index={0}
            reduced={reduced}
          />
          <StatCard
            icon={<TrendingUp className="size-3.5" />}
            label="Predicted Month"
            value={114320}
            color="text-violet"
            index={1}
            reduced={reduced}
          />
          <StatCard
            icon={<Zap className="size-3.5" />}
            label="Potential Savings"
            value={18750}
            color="text-emerald-400"
            index={2}
            reduced={reduced}
          />
          <StatCard
            icon={<Activity className="size-3.5" />}
            label="Active Anomalies"
            value={4}
            color="text-ember"
            index={3}
            reduced={reduced}
          />
        </div>

        {/* Mini bar chart */}
        <div
          className={cn(
            "rounded-lg border border-white/[0.06] bg-white/[0.02] p-2.5 transition-all duration-400",
          )}
        >
          <p className="mb-1.5 text-[11px] text-white/40 font-mono">Daily cost trend (past 12 days)</p>
          <div className="flex items-end gap-1 h-16">
            {bars.map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm bg-gradient-to-t from-cyan/60 to-cyan/30 transition-all duration-500"
                style={{
                  height: `${h}%`,
                  transitionDelay: `${i * 40}ms`,
                  opacity: reduced ? 1 : 0,
                  animation: reduced ? "none" : `fade-up 300ms var(--ease-out-expo) ${i * 40}ms forwards`,
                }}
              />
            ))}
          </div>
        </div>

        {/* Anomaly alert */}
        <div
          className={cn(
            "rounded-lg border border-ember/20 bg-ember/[0.06] p-3 transition-all duration-500",
            !alertVisible && "opacity-0 translate-y-2",
            alertVisible && "opacity-100 translate-y-0",
          )}
          style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
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
        </div>

        {/* Savings recommendation */}
        <div
          className={cn(
            "rounded-lg border border-cyan/20 bg-cyan/[0.04] p-3 transition-all duration-500",
            !showRec && "opacity-0 translate-y-2",
            showRec && "opacity-100 translate-y-0",
          )}
          style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
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
        </div>
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
    <section className="relative min-h-[100dvh] flex items-center bg-[#0A0E1A] overflow-hidden pt-14">
      <AmbientOrbs />
      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 py-8 md:py-16">
        <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
          {/* Left: text */}
          <div
            className={cn("max-w-xl", reduced ? "" : "opacity-0")}
            style={{
              animation: reduced ? "none" : "fade-up 500ms var(--ease-out-expo) 100ms forwards",
            }}
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
                className="bg-cyan text-space font-semibold hover:brightness-110 text-base px-8 h-12"
                nativeButton={false}
                render={<a href="/signup" />}
              >
                Get Started
                <ArrowRight className="ml-2 size-4" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white/10 text-white/80 hover:text-white hover:bg-white/[0.06] text-base px-8 h-12"
                onClick={scrollToDemo}
              >
                Live Demo
              </Button>
            </div>
          </div>

          {/* Right: dashboard mockup */}
          <div
            className={cn(
              "w-full max-w-lg mx-auto lg:mx-0 lg:max-w-none",
              reduced ? "" : "opacity-0",
            )}
            style={{
              animation: reduced ? "none" : "fade-up 500ms var(--ease-out-expo) 200ms forwards",
            }}
          >
            <HeroDashboard reduced={reduced} />
          </div>
        </div>
      </div>
    </section>
  );
}
