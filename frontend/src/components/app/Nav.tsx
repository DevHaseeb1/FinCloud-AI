"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, CloudUpload, Gauge, Radar, Sparkles, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

type NavItem = {
  href: string;
  label: string;
  icon: React.ReactNode;
};

const items: NavItem[] = [
  { href: "/", label: "Dashboard", icon: <Gauge className="size-4" /> },
  { href: "/cost", label: "Cost Analytics", icon: <BarChart3 className="size-4" /> },
  { href: "/anomalies", label: "Anomalies", icon: <TriangleAlert className="size-4" /> },
  { href: "/forecast", label: "Forecast", icon: <Radar className="size-4" /> },
  { href: "/recommendations", label: "Recommendations", icon: <Sparkles className="size-4" /> },
  { href: "/upload", label: "Upload", icon: <CloudUpload className="size-4" /> },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="grid gap-1">
      {items.map((it) => {
        const active = pathname === it.href;
        return (
          <Link
            key={it.href}
            href={it.href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              active && "bg-accent text-accent-foreground",
            )}
          >
            {it.icon}
            <span>{it.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

