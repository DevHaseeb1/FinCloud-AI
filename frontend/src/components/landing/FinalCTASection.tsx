"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, Cloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils";

export function FinalCTASection() {
  const reduced = useReducedMotion();

  return (
    <section className="relative overflow-hidden bg-[#0A0E1A] py-20 md:py-32">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan/5 via-transparent to-violet/5" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-[600px] rounded-full bg-cyan/[0.03] blur-3xl" />

      <div
        className={cn(
          "relative z-10 mx-auto max-w-3xl px-6 text-center",
          reduced ? "" : "opacity-0",
        )}
        style={{
          animation: reduced ? "none" : "fade-up 500ms var(--ease-out-expo) 100ms forwards",
        }}
      >
        <h2 className="text-3xl font-bold text-white md:text-5xl leading-tight">
          Reduce Cloud Cost with{" "}
          <span className="bg-gradient-to-r from-cyan to-violet bg-clip-text text-transparent">AI</span>
        </h2>
        <p className="mt-4 text-lg text-white/60 max-w-2xl mx-auto">
          Detect anomalies, forecast spending, and uncover savings opportunities before they impact your budget.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Button
            size="lg"
            className="bg-cyan text-space font-semibold hover:brightness-110 text-base px-8 h-12"
            nativeButton={false}
            render={<a href="/signup" />}
          >
            Create Account
            <ArrowRight className="ml-2 size-4" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white/10 text-white/80 hover:text-white hover:bg-white/[0.06] text-base px-8 h-12"
            nativeButton={false}
            render={<a href="/aws" />}
          >
            <Cloud className="mr-2 size-4" />
            Connect AWS
          </Button>
        </div>
      </div>
    </section>
  );
}
