"use client";

import * as React from "react";
import { usePathname } from "next/navigation";

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const prevPathRef = React.useRef(pathname);
  const [state, setState] = React.useState<"idle" | "exit" | "enter">("idle");
  const [displayChildren, setDisplayChildren] = React.useState(children);

  React.useEffect(() => {
    if (pathname === prevPathRef.current) return;
    prevPathRef.current = pathname;
    setState("exit");
    const exitTimer = setTimeout(() => {
      setDisplayChildren(children);
      setState("enter");
      const enterTimer = setTimeout(() => {
        setState("idle");
      }, 250);
      return () => clearTimeout(enterTimer);
    }, 150);
    return () => clearTimeout(exitTimer);
  }, [pathname, children]);

  React.useEffect(() => {
    setDisplayChildren(children);
  }, [children]);

  return (
    <div
      className={
        state === "exit"
          ? "opacity-0 translate-y-2 transition-all duration-150"
          : state === "enter"
            ? "opacity-0 -translate-y-2"
            : "opacity-100 translate-y-0 transition-all duration-250"
      }
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      {displayChildren}
    </div>
  );
}
