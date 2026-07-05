"use client";

import {
  useMotionValue,
  animate,
  type Variants,
  type Transition,
} from "framer-motion";
import { useState, useEffect } from "react";

/* ── Transition presets ─────────────────────────────────────── */

export const springTransition: Transition = {
  type: "spring",
  stiffness: 100,
  damping: 15,
};

export const easeOutExpo: Transition = {
  duration: 0.5,
  ease: [0.16, 1, 0.3, 1],
};

/* ── Framer Motion variants ────────────────────────────────── */

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: easeOutExpo,
  },
};

export const fadeUpDelayed = (delay: number): Variants => ({
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { ...easeOutExpo, delay },
  },
});

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: springTransition,
  },
};

export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: easeOutExpo,
  },
};

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerContainerFast: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.06,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: easeOutExpo,
  },
};

/* ── Page transition variants ──────────────────────────────── */

export const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.15 },
  },
};

/* ── Count-up hook (Framer Motion) ─────────────────────────── */

export function useCountUp(
  target: number,
  duration: number = 1000,
  disabled: boolean = false,
): number {
  const motionValue = useMotionValue(0);
  const [display, setDisplay] = useState(() => (disabled ? target : 0));

  useEffect(() => {
    if (disabled) {
      motionValue.set(target);
      // Use rAF to avoid setState-in-effect lint warning
      const id = requestAnimationFrame(() => setDisplay(target));
      return () => cancelAnimationFrame(id);
    }
    motionValue.set(0);
    setDisplay(0);
    const controls = animate(motionValue, target, {
      duration: duration / 1000,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (latest) => setDisplay(Math.round(latest)),
    });
    return () => controls.stop();
  }, [target, duration, disabled, motionValue]);

  return display;
}

/* ── Backward-compatible staggerDelay ──────────────────────── */

export function staggerDelay(index: number, base: number = 60): number {
  return index * base;
}
