"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Menu, Search, ChevronLeft, ChevronRight, User, LogOut } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Nav } from "@/components/app/Nav";
import { ThemeToggle } from "@/components/app/ThemeToggle";
import { AmbientBackground } from "@/components/shell/AmbientBackground";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout } = useAuth();
  const [collapsed, setCollapsed] = React.useState(false);
  const [menuOpen, setMenuOpen] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement>(null);
  const sidebarWidth = collapsed ? "w-16" : "w-64";

  React.useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "?";

  return (
    <div className="flex h-full w-full bg-background overflow-x-hidden">
      <AmbientBackground />
      <aside
        className={`hidden flex-col border-r border-sidebar-border bg-sidebar p-4 transition-all duration-250 md:flex ${sidebarWidth}`}
        style={{ transitionTimingFunction: "var(--ease-in-out-circ)" }}
      >
        <Link href="/dashboard" className="flex items-center gap-2 px-2 py-1">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-cyan to-violet">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 14.5a4 4 0 0 1 2.5-7 5.5 5.5 0 0 1 10.2-1.7A4.5 4.5 0 0 1 18 14.5H6a1 1 0 0 1-1-1z" fill="white" opacity="0.9" />
              <path d="M9 14.5v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3M12 10.5v-3M8 17.5h8M9.5 17.5l-1 3M14.5 17.5l1 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
            </svg>
          </div>
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
                <Link href="/dashboard" className="flex items-center gap-2">
                  <div className="flex size-8 items-center justify-center rounded-md bg-gradient-to-br from-cyan to-violet">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M5 14.5a4 4 0 0 1 2.5-7 5.5 5.5 0 0 1 10.2-1.7A4.5 4.5 0 0 1 18 14.5H6a1 1 0 0 1-1-1z" fill="white" opacity="0.9" />
                      <path d="M9 14.5v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3M12 10.5v-3M8 17.5h8M9.5 17.5l-1 3M14.5 17.5l1 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
                    </svg>
                  </div>
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
            {isAuthenticated && user ? (
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex size-8 items-center justify-center rounded-full bg-violet text-white text-sm font-semibold transition-transform duration-100 hover:scale-110 active:scale-95"
                  aria-label="User menu"
                >
                  {initials}
                </button>
                {menuOpen && (
                  <div
                    className="absolute right-0 top-10 z-50 w-48 rounded-xl border border-white/8 bg-surface p-1 shadow-lg"
                    style={{
                      animation: "fade-up 150ms var(--ease-out-expo)",
                    }}
                  >
                    <Link
                      href="/profile"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-foreground hover:bg-muted transition-colors duration-100"
                    >
                      <User className="size-4" />
                      Profile
                    </Link>
                    <Separator className="my-1" />
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        logout();
                      }}
                      className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-ember hover:bg-destructive/10 transition-colors duration-100"
                    >
                      <LogOut className="size-4" />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Sign in
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button variant="default" size="sm">
                    Sign up
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </header>

        <main className="relative z-10 flex-1 overflow-x-hidden overflow-y-auto px-4 py-6 md:px-6">{children}</main>
      </div>
    </div>
  );
}
