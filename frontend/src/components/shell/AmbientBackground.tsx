"use client";

import { useReducedMotion } from "@/hooks/useReducedMotion";

export function AmbientBackground() {
  const reduced = useReducedMotion();

  if (reduced) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden contain-strict">
      <div
        className="absolute -top-32 -left-32 size-96 rounded-full opacity-[0.05] dark:opacity-[0.05]"
        style={{
          background: "radial-gradient(circle, var(--cyan) 0%, transparent 70%)",
          animation: "particle-drift 8s ease-in-out infinite",
        }}
      />
      <div
        className="absolute -bottom-32 -right-32 size-96 rounded-full opacity-[0.04] dark:opacity-[0.04]"
        style={{
          background: "radial-gradient(circle, var(--violet) 0%, transparent 70%)",
          animation: "particle-drift 11s ease-in-out infinite",
          animationDelay: "2s",
        }}
      />
      <div
        className="absolute top-1/2 right-0 size-80 rounded-full opacity-[0.03] dark:opacity-[0.03]"
        style={{
          background: "radial-gradient(circle, var(--ember) 0%, transparent 70%)",
          animation: "particle-drift 9s ease-in-out infinite",
          animationDelay: "5s",
        }}
      />
    </div>
  );
}
