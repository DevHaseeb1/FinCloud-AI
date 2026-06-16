"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, CloudUpload, Gauge, Radar, Sparkles, TriangleAlert, Cloud } from "lucide-react";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";

type NavItem = {
  href: string;
  label: string;
  icon: React.ReactNode;
};

const mainItems: NavItem[] = [
  { href: "/", label: "Dashboard", icon: <Gauge className="size-4" /> },
  { href: "/cost", label: "Cost Analytics", icon: <BarChart3 className="size-4" /> },
  { href: "/anomalies", label: "Anomalies", icon: <TriangleAlert className="size-4" /> },
  { href: "/forecast", label: "Forecast", icon: <Radar className="size-4" /> },
  { href: "/recommendations", label: "Recommendations", icon: <Sparkles className="size-4" /> },
];

const secondaryItems: NavItem[] = [
  { href: "/aws", label: "AWS Connections", icon: <Cloud className="size-4" /> },
  { href: "/upload", label: "Upload", icon: <CloudUpload className="size-4" /> },
];

function NavItemLink({ it, collapsed, mounted, pathname, delay }: { it: NavItem; collapsed?: boolean; mounted: boolean; pathname: string; delay: number }) {
  const active = pathname === it.href || (it.href !== "/" && pathname.startsWith(it.href));
  return (
    <Link
      href={it.href}
      className={cn(
        "flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-100 relative overflow-hidden",
        active && "bg-primary/10 text-primary font-medium",
        !mounted && "opacity-0 translate-x-[-12px]",
        mounted && "opacity-100 translate-x-0",
      )}
      style={{
        transitionProperty: "opacity, transform, background-color, color",
        transitionDuration: "250ms",
        transitionTimingFunction: "var(--ease-out-expo)",
        transitionDelay: mounted ? `${delay}ms` : "0ms",
      }}
    >
      {active && (
        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-cyan transition-transform duration-150 origin-bottom scale-y-100" />
      )}
      <span className={cn("shrink-0", active ? "text-cyan" : "text-muted-foreground")}>{it.icon}</span>
      {!collapsed && (
        <span
          className="transition-opacity duration-100"
          style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
        >
          {it.label}
        </span>
      )}
      {active && !collapsed && (
        <span className="ml-auto text-[10px] font-medium text-cyan/70">Live</span>
      )}
    </Link>
  );
}

export function Nav({ collapsed }: { collapsed?: boolean }) {
  const pathname = usePathname();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <nav className="grid gap-1">
      {mainItems.map((it, i) => (
        <NavItemLink key={it.href} it={it} collapsed={collapsed} mounted={mounted} pathname={pathname} delay={i * 30} />
      ))}
      <div className="my-2">
        <Separator />
      </div>
      {secondaryItems.map((it, i) => (
        <NavItemLink key={it.href} it={it} collapsed={collapsed} mounted={mounted} pathname={pathname} delay={(mainItems.length + i) * 30} />
      ))}
    </nav>
  );
}
