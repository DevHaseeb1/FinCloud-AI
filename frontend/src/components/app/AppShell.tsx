"use client";

import * as React from "react";
import Link from "next/link";
import { Menu, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Nav } from "@/components/app/Nav";
import { ThemeToggle } from "@/components/app/ThemeToggle";
import { AmbientBackground } from "@/components/shell/AmbientBackground";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = React.useState(false);
  const sidebarWidth = collapsed ? "w-16" : "w-64";

  return (
    <div className="flex min-h-[100dvh] w-full bg-background">
      <AmbientBackground />
      <aside
        className={`hidden flex-col border-r border-sidebar-border bg-sidebar p-4 transition-all duration-250 md:flex ${sidebarWidth}`}
        style={{ transitionTimingFunction: "var(--ease-in-out-circ)" }}
      >
        <Link href="/" className="flex items-center gap-2 px-2 py-1">
          <div className="size-8 shrink-0 rounded-md bg-gradient-to-br from-cyan to-violet" />
          <div
            className={`flex flex-col leading-tight transition-opacity duration-100 ${
              collapsed ? "opacity-0 w-0 overflow-hidden" : "opacity-100"
            }`}
          >
            <span className="text-sm font-semibold text-sidebar-foreground">FinCloud-AI</span>
            <span className="text-xs text-muted-foreground">FinOps Dashboard</span>
          </div>
        </Link>
        <Separator className="my-4" />
        <Nav collapsed={collapsed} />
        <div className="mt-auto pt-4">
          <Separator className="mb-4" />
          <div className="flex items-center justify-between gap-2">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="flex items-center justify-center size-8 rounded-md text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-100"
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {collapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
            </button>
            <ThemeToggle />
          </div>
        </div>
      </aside>

      <div className="relative z-10 flex flex-1 flex-col">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border/50 bg-background/80 px-4 py-3 backdrop-blur-lg transition-colors duration-300">
          <Sheet>
            <SheetTrigger className="md:hidden" aria-label="Open navigation">
              <Menu className="size-5" />
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <div className="mb-4">
                <Link href="/" className="flex items-center gap-2">
                  <div className="size-8 rounded-md bg-gradient-to-br from-cyan to-violet" />
                  <div className="flex flex-col leading-tight">
                    <span className="text-sm font-semibold">FinCloud-AI</span>
                    <span className="text-xs text-muted-foreground">FinOps Dashboard</span>
                  </div>
                </Link>
              </div>
              <Nav />
              <div className="mt-6 flex items-center justify-end gap-2">
                <ThemeToggle />
              </div>
            </SheetContent>
          </Sheet>

          <div className="relative flex w-full max-w-lg items-center gap-2">
            <Search className="pointer-events-none absolute left-3 size-4 text-muted-foreground" />
            <Input
              placeholder="Search services, regions, alerts…"
              className="pl-9 transition-all duration-200 focus-within:shadow-[0_0_0_2px_rgba(0,212,255,0.3)]"
              style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
              aria-label="Search"
            />
          </div>

          <div className="ml-auto hidden items-center gap-2 md:flex">
            <ThemeToggle />
          </div>
        </header>

        <main className="relative z-10 flex-1 px-4 py-6 md:px-6">{children}</main>
      </div>
    </div>
  );
}
