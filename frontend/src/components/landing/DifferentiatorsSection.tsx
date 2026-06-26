"use client";

import * as React from "react";
import { BarChart3, Brain, GitCompare, Radio } from "lucide-react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { staggerDelay } from "@/lib/animations";
import { cn } from "@/lib/utils";

const DIFFERENTIATORS = [
  {
    icon: GitCompare,
    title: "Account-Normalized Anomaly Detection",
    subtitle: "Most tools use global thresholds.",
    description: "FinCloud-AI learns the normal spending behavior of each account, service, region, environment, and instance type — then detects anomalies relative to that baseline.",
    tags: ["Account", "Service", "Region", "Environment", "Instance Type"],
    gradient: "from-cyan to-blue-500",
  },
  {
    icon: Brain,
    title: "Triple AI Engine",
    subtitle: "Most solutions offer one AI feature.",
    description: "FinCloud-AI combines Isolation Forest for anomaly detection, Facebook Prophet for cost forecasting, and Random Forest for cost optimization inside a single processing pipeline.",
    gradient: "from-violet to-purple-500",
    flow: true,
  },
  {
    icon: BarChart3,
    title: "Cost-Per-Unit Intelligence",
    subtitle: "Instead of asking: Did cost increase?",
    description: "FinCloud-AI asks: Did cost increase without usage increasing? This catches misconfigured instances, inefficient workloads, and resource waste before bills explode.",
    gradient: "from-ember to-orange-500",
  },
  {
    icon: Radio,
    title: "Real-Time Streaming Analysis",
    subtitle: "Animated architecture pipeline",
    description: "AWS Billing data flows through Kinesis Streams to Lambda consumers for ML inference, generating alerts and dashboard updates in real time.",
    gradient: "from-emerald-400 to-teal-500",
    pipeline: true,
  },
];

function DifferentiatorCard({
  item,
  index,
  reduced,
}: {
  item: (typeof DIFFERENTIATORS)[number];
  index: number;
  reduced: boolean;
}) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (reduced) { setVisible(true); return; }
    const t = setTimeout(() => setVisible(true), staggerDelay(index, 120));
    return () => clearTimeout(t);
  }, [index, reduced]);

  return (
    <div
      className={cn(
        "rounded-xl border border-white/[0.06] bg-[#0D1225] p-6 transition-all duration-500 hover:border-white/[0.12] hover:shadow-[0_0_32px_rgba(0,212,255,0.06)]",
        !visible && "opacity-0 translate-y-6",
        visible && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className={cn("mb-4 flex size-10 items-center justify-center rounded-lg bg-gradient-to-br", item.gradient)}>
        <item.icon className="size-5 text-white" />
      </div>
      <p className="text-xs text-white/40 uppercase tracking-wider font-medium">{item.subtitle}</p>
      <h3 className="mt-1 text-lg font-semibold text-white">{item.title}</h3>
      <p className="mt-2 text-sm text-white/60 leading-relaxed">{item.description}</p>

      {/* Tags */}
      {item.tags && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {item.tags.map((tag) => (
            <span key={tag} className="inline-flex rounded-full border border-cyan/20 bg-cyan/[0.04] px-2 py-0.5 text-[11px] text-cyan font-medium">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* AI Flow diagram */}
      {item.flow && (
        <div className="mt-4 space-y-1.5">
          {["Isolation Forest", "Facebook Prophet", "Random Forest"].map((name, i) => (
            <div key={name} className="flex items-center gap-2 text-xs">
              <div className={cn(
                "size-1.5 rounded-full",
                i === 0 ? "bg-cyan" : i === 1 ? "bg-violet" : "bg-emerald-400",
              )} />
              <span className="text-white/70">{name}</span>
              {i < 2 && <span className="text-white/20">↓</span>}
            </div>
          ))}
          <div className="mt-1 flex gap-2 text-[11px]">
            <span className="rounded bg-cyan/10 px-1.5 py-0.5 text-cyan">Anomaly Detection</span>
            <span className="rounded bg-violet/10 px-1.5 py-0.5 text-violet">Cost Forecasting</span>
            <span className="rounded bg-emerald-400/10 px-1.5 py-0.5 text-emerald-400">Cost Optimization</span>
          </div>
        </div>
      )}

      {/* Pipeline diagram */}
      {item.pipeline && (
        <div className="mt-4 space-y-1">
          {["AWS Billing", "Kinesis Stream", "Lambda Consumer", "ML Inference", "Alerts & Dashboard"].map((step, i) => (
            <div key={step} className="flex items-center gap-2 text-xs">
              <div className="size-1.5 rounded-full bg-cyan/60" />
              <span className={i === 4 ? "text-cyan font-medium" : "text-white/60"}>{step}</span>
              {i < 4 && <span className="text-white/20 ml-auto">↓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function DifferentiatorsSection() {
  const reduced = useReducedMotion();

  return (
    <section className="bg-[#0A0E1A] py-20 md:py-28">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white md:text-4xl">
            Why FinCloud-AI Is Different
          </h2>
          <p className="mt-3 text-white/50 max-w-2xl mx-auto">
            Most cloud cost tools only show you what you spent. FinCloud-AI tells you what went wrong, what will happen next, and how to fix it — with ML-driven precision.
          </p>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {DIFFERENTIATORS.map((item, i) => (
            <DifferentiatorCard key={item.title} item={item} index={i} reduced={reduced} />
          ))}
        </div>
      </div>
    </section>
  );
}
