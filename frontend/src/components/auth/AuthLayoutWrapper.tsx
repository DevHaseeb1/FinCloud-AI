"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { AppShell } from "@/components/app/AppShell";
import { PageTransition } from "@/components/shell/PageTransition";

const AUTH_PATHS = ["/login", "/signup"];

export function AuthLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthPage = AUTH_PATHS.includes(pathname);

  if (isAuthPage) {
    return <>{children}</>;
  }

  return (
    <AppShell>
      <PageTransition>{children}</PageTransition>
    </AppShell>
  );
}
