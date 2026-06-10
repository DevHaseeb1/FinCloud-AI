"use client";

import { useState, useEffect, useRef, useCallback } from "react";

export function staggerDelay(index: number, base: number = 60): number {
  return index * base;
}

export function useCountUp(
  target: number,
  duration: number = 800,
  disabled: boolean = false,
): number {
  const [value, setValue] = useState(disabled ? target : 0);
  const rafRef = useRef<number>(0);
  const startTimeRef = useRef<number>(0);

  const animate = useCallback(() => {
    if (!startTimeRef.current) startTimeRef.current = performance.now();
    const elapsed = performance.now() - startTimeRef.current;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    setValue(Math.round(eased * target));
    if (progress < 1) {
      rafRef.current = requestAnimationFrame(animate);
    } else {
      setValue(target);
    }
  }, [target, duration]);

  useEffect(() => {
    if (disabled) {
      setValue(target);
      return;
    }
    startTimeRef.current = 0;
    setValue(0);
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, animate, disabled]);

  return value;
}
