"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { PageTransition } from "@/components/shell/PageTransition";

const NO_SHELL_PATHS = ["/login", "/signup", "/"];

export function AuthLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const noShell = NO_SHELL_PATHS.includes(pathname);

  if (noShell) {
    return <>{children}</>;
  }

  return (
    <AppShell>
      <PageTransition>{children}</PageTransition>
    </AppShell>
  );
}
