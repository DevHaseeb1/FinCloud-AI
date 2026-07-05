"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, Cloud } from "lucide-react";
import { motion, useInView } from "framer-motion";
import { Button } from "@/components/ui/button";
import { fadeUp } from "@/lib/animations";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export function FinalCTASection() {
  const reduced = useReducedMotion();
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="relative overflow-hidden bg-background py-20 md:py-32">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan/5 via-transparent to-violet/5" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-[600px] rounded-full bg-cyan/[0.03] blur-3xl" />

      <motion.div
        ref={ref}
        className="relative z-10 mx-auto max-w-3xl px-6 md:px-20 text-center"
        initial={reduced ? false : "hidden"}
        animate={reduced || isInView ? "visible" : "hidden"}
        variants={fadeUp}
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
            className="bg-cyan text-space font-semibold hover:brightness-110 text-base px-8 h-12 hover:scale-[1.02] active:scale-[0.98] transition-transform"
            nativeButton={false}
            render={<Link href="/signup" />}
          >
            Create Account
            <ArrowRight className="ml-2 size-4" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white/10 text-white/80 hover:text-white hover:bg-white/[0.06] text-base px-8 h-12 hover:scale-[1.02] active:scale-[0.98] transition-transform"
            nativeButton={false}
            render={<Link href="/aws" />}
          >
            <Cloud className="mr-2 size-4" />
            Connect AWS
          </Button>
        </div>
      </motion.div>
    </section>
  );
}
