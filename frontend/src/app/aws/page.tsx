"use client";

import * as React from "react";
import { Plus, Cloud } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ConnectionCard } from "@/components/aws/ConnectionCard";
import { ConnectionWizard } from "@/components/aws/ConnectionWizard";
import * as awsService from "@/services/awsService";
import type { AwsConnection } from "@/types/apiTypes";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export default function AwsPage() {
  const reduced = useReducedMotion();
  const [connections, setConnections] = React.useState<AwsConnection[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [wizardOpen, setWizardOpen] = React.useState(false);
  const [syncingId, setSyncingId] = React.useState<number | null>(null);

  const loadConnections = React.useCallback(async () => {
    try {
      const res = await awsService.listConnections();
      setConnections(res.connections || []);
    } catch (e) {
      console.error("Failed to load connections", e);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadConnections();
  }, [loadConnections]);

  const handleSync = async (id: number) => {
    setSyncingId(id);
    try {
      await awsService.fetchBillingData({ connection_id: id });
      await loadConnections();
    } catch (e) {
      console.error("Sync failed", e);
    } finally {
      setSyncingId(null);
    }
  };

  const handleDelete = async (conn: AwsConnection) => {
    if (!window.confirm(`Delete connection "${conn.name}"? This will stop all syncs. Existing cost data will be preserved.`)) return;
    try {
      await awsService.deleteConnection(conn.id);
      await loadConnections();
    } catch (e) {
      console.error("Delete failed", e);
    }
  };

  return (
    <ProtectedRoute>
      <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground" style={{ fontFamily: "var(--font-sans)", fontWeight: 700 }}>
                AWS Connections
              </h1>
              <p className="text-sm text-muted-foreground">Manage your AWS account integrations</p>
            </div>
            {connections.length > 0 && (
              <button
                onClick={() => setWizardOpen(true)}
                className="flex items-center gap-2 h-8 px-3 rounded-lg border border-border bg-background text-sm text-foreground hover:bg-muted transition-all duration-100"
              >
                <Plus className="size-4" />
                Add connection
              </button>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="size-6 rounded-full border-2 border-cyan/30 border-t-cyan animate-spin" />
            </div>
          ) : connections.length === 0 ? (
            <div
              className="flex flex-col items-center justify-center py-20 gap-4"
              style={{ animation: reduced ? "none" : "fade-up 320ms var(--ease-out-expo)" }}
            >
              <svg
                width="96"
                height="64"
                viewBox="0 0 96 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-cyan/30"
              >
                <rect x="12" y="8" width="72" height="48" rx="8" stroke="currentColor" strokeWidth="1.5" fill="none" />
                <path d="M48 8v48M28 8v48M68 8v48" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                <path d="M24 24h8M24 32h8M24 40h8M64 24h8M64 32h8M64 40h8" stroke="currentColor" strokeWidth="1" opacity="0.5" />
                <path d="M36 20h24M36 28h24M36 36h24" stroke="currentColor" strokeWidth="0.5" opacity="0.2" />
                <path d="M20 56l4-6h48l4 6" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.4" />
              </svg>
              <h2 className="text-lg font-semibold text-foreground" style={{ fontFamily: "var(--font-sans)", fontWeight: 700 }}>
                No AWS accounts connected
              </h2>
              <p className="text-sm text-muted-foreground">Connect an account to start pulling real cost data</p>
              <button
                onClick={() => setWizardOpen(true)}
                className="py-3 px-6 rounded-lg bg-cyan text-space font-semibold text-sm hover:bg-cyan/90 transition-all duration-100"
                style={{ fontFamily: "var(--font-sans)", fontWeight: 600 }}
              >
                Connect AWS Account
              </button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {connections.map((conn, i) => (
                <ConnectionCard
                  key={conn.id}
                  connection={conn}
                  index={i}
                  onSync={handleSync}
                  onEdit={() => {}}
                  onDelete={handleDelete}
                  syncing={syncingId === conn.id}
                />
              ))}
            </div>
          )}
        </div>

        <ConnectionWizard
          open={wizardOpen}
          onClose={() => setWizardOpen(false)}
          onComplete={() => {
            setWizardOpen(false);
            loadConnections();
          }}
        />
    </ProtectedRoute>
  );
}
