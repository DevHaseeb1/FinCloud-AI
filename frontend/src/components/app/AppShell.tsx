"use client";

import Link from "next/link";
import { Menu, Search } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Nav } from "@/components/app/Nav";
import { ThemeToggle } from "@/components/app/ThemeToggle";
import { ModeToggle } from "@/components/app/ModeToggle";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[100dvh] w-full bg-background">
      <aside className="hidden w-64 flex-col border-r bg-card p-4 md:flex">
        <Link href="/" className="flex items-center gap-2 px-2 py-1">
          <div className="size-8 rounded-md bg-primary" />
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold">FinCloud-AI</span>
            <span className="text-xs text-muted-foreground">FinOps Dashboard</span>
          </div>
        </Link>
        <Separator className="my-4" />
        <Nav />
        <div className="mt-auto pt-4">
          <Separator className="mb-4" />
          <div className="flex items-center justify-between gap-2">
            <ModeToggle />
            <ThemeToggle />
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b bg-background/80 px-4 py-3 backdrop-blur">
          <Sheet>
            <SheetTrigger className="md:hidden" aria-label="Open navigation">
              <Menu className="size-5" />
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <div className="mb-4">
                <Link href="/" className="flex items-center gap-2">
                  <div className="size-8 rounded-md bg-primary" />
                  <div className="flex flex-col leading-tight">
                    <span className="text-sm font-semibold">FinCloud-AI</span>
                    <span className="text-xs text-muted-foreground">FinOps Dashboard</span>
                  </div>
                </Link>
              </div>
              <Nav />
              <div className="mt-6 flex items-center justify-between gap-2">
                <ModeToggle />
                <ThemeToggle />
              </div>
            </SheetContent>
          </Sheet>

          <div className="relative flex w-full max-w-lg items-center gap-2">
            <Search className="pointer-events-none absolute left-3 size-4 text-muted-foreground" />
            <Input
              placeholder="Search services, regions, alerts…"
              className="pl-9"
              aria-label="Search"
            />
          </div>

          <div className="ml-auto hidden items-center gap-2 md:flex">
            <ModeToggle />
            <ThemeToggle />
          </div>
        </header>

        <main className="flex-1 px-4 py-6 md:px-6">{children}</main>
      </div>
    </div>
  );
}

