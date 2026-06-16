"use client";

import * as React from "react";
import Link from "next/link";
import { RefreshCw, Pencil, Trash2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import type { AwsConnection } from "@/types/apiTypes";

interface ConnectionCardProps {
  connection: AwsConnection;
  index: number;
  onSync: (id: number) => void;
  onEdit: (conn: AwsConnection) => void;
  onDelete: (conn: AwsConnection) => void;
  syncing: boolean;
}

export function ConnectionCard({ connection, index, onSync, onEdit, onDelete, syncing }: ConnectionCardProps) {
  const reduced = useReducedMotion();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    const t = setTimeout(() => setMounted(true), reduced ? 0 : index * 60);
    return () => clearTimeout(t);
  }, [index, reduced]);

  const isError = connection.last_fetch_status === "error" || connection.last_fetch_status?.startsWith("error");

  return (
    <div
      className={cn(
        "bg-surface border border-white/8 rounded-xl p-4 flex flex-col gap-3 transition-all duration-250",
        !mounted && "opacity-0 translate-y-4",
        mounted && "opacity-100 translate-y-0",
      )}
      style={{ transitionTimingFunction: "var(--ease-out-expo)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="size-4 rounded-sm bg-[#FF9900] shrink-0" />
          <span className="text-sm font-semibold text-foreground" style={{ fontFamily: "var(--font-sans)", fontWeight: 600 }}>
            {connection.name}
          </span>
        </div>
        <span
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
            isError
              ? "bg-ember/15 text-ember"
              : "bg-emerald-500/15 text-emerald-400",
            isError && "animate-anomaly-pulse",
          )}
        >
          {isError ? "Error" : "Active"}
        </span>
      </div>

      <div className="space-y-1 text-sm">
        {connection.account_id && (
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-xs">Account ID:</span>
            <span className="font-mono text-xs text-muted-foreground">{connection.account_id}</span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Region:</span>
          <span className="font-mono text-xs text-muted-foreground">{connection.region}</span>
        </div>
        {connection.last_fetch_at && (
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-xs">Last synced:</span>
            <span className="text-xs text-muted-foreground">
              {new Date(connection.last_fetch_at).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3 pt-1 border-t border-white/8">
        <button
          onClick={() => onSync(connection.id)}
          disabled={syncing}
          className="flex items-center gap-1.5 text-xs text-cyan hover:text-cyan/80 transition-colors duration-100 disabled:opacity-50"
        >
          {syncing ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <RefreshCw className="size-3.5" />
          )}
          Sync now
        </button>
        <button
          onClick={() => onEdit(connection)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors duration-100"
        >
          <Pencil className="size-3.5" />
        </button>
        <button
          onClick={() => onDelete(connection)}
          className="text-xs text-muted-foreground hover:text-ember transition-colors duration-100 ml-auto"
        >
          <Trash2 className="size-3.5" />
        </button>
        <Link
          href={`/aws/${connection.id}`}
          className="text-xs text-muted-foreground hover:text-cyan transition-colors duration-100"
        >
          View
        </Link>
      </div>
    </div>
  );
}
