"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { RefreshCw, Loader2, Trash2 } from "lucide-react";
import { subDays } from "date-fns";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DateRangePicker } from "@/components/filters/DateRangePicker";
import { cn } from "@/lib/utils";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import * as awsService from "@/services/awsService";
import type { AwsConnection, AwsFetchHistory } from "@/types/apiTypes";

export default function AwsConnectionDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const reduced = useReducedMotion();

  const [connection, setConnection] = React.useState<AwsConnection | null>(null);
  const [history, setHistory] = React.useState<AwsFetchHistory[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [fetching, setFetching] = React.useState(false);
  const [fetchStep, setFetchStep] = React.useState("");
  const [fetchRange, setFetchRange] = React.useState<{ from?: Date; to?: Date }>({
    from: subDays(new Date(), 90),
    to: new Date(),
  });
  const [useCur, setUseCur] = React.useState(false);
  const [deleteModal, setDeleteModal] = React.useState(false);

  const loadData = React.useCallback(async () => {
    try {
      const [connRes, histRes] = await Promise.all([
        awsService.getConnection(id),
        awsService.getFetchHistory(id),
      ]);
      setConnection(connRes.connection);
      setHistory(histRes.history || []);
    } catch (e) {
      console.error("Failed to load connection", e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFetch = async () => {
    setFetching(true);
    setFetchStep(useCur ? "Fetching from CUR\u2026" : "Fetching from Cost Explorer\u2026");
    try {
      await awsService.fetchBillingData({
        connection_id: id,
        start_date: fetchRange.from?.toISOString().split("T")[0],
        end_date: fetchRange.to?.toISOString().split("T")[0],
        use_cur: useCur,
      });
      setFetchStep("Running ETL\u2026");
      await new Promise((r) => setTimeout(r, 500));
      await loadData();
      setFetchStep("");
    } catch (e) {
      setFetchStep("Fetch failed");
    } finally {
      setFetching(false);
    }
  };

  const handleDelete = async () => {
    try {
      await awsService.deleteConnection(id);
      window.location.href = "/aws";
    } catch (e) {
      console.error("Delete failed", e);
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="flex items-center justify-center py-20">
          <div className="size-6 rounded-full border-2 border-cyan/30 border-t-cyan animate-spin" />
        </div>
      </ProtectedRoute>
    );
  }

  if (!connection) {
    return (
      <ProtectedRoute>
        <div className="text-center py-20">
          <p className="text-muted-foreground">Connection not found</p>
          <Link href="/aws" className="text-cyan text-sm mt-2 inline-block">Back to AWS Connections</Link>
        </div>
      </ProtectedRoute>
    );
  }

  const isError = connection.last_fetch_status === "error" || connection.last_fetch_status?.startsWith("error");

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link href="/aws" className="hover:text-foreground transition-colors duration-100">AWS Connections</Link>
          <span>/</span>
          <span className="text-foreground">{connection.name}</span>
        </div>

        <div className="bg-surface border border-white/8 rounded-xl p-4 space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className="size-4 rounded-sm bg-[#FF9900]" />
              <h2 className="text-base font-semibold text-foreground">{connection.name}</h2>
            </div>
            <span
              className={cn(
                "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                isError ? "bg-ember/15 text-ember" : "bg-emerald-500/15 text-emerald-400",
                isError && "animate-anomaly-pulse",
              )}
            >
              {isError ? "Error" : "Active"}
            </span>
          </div>

          <div className="grid gap-2 sm:grid-cols-2 text-sm">
            <div>
              <span className="text-xs text-muted-foreground">Account ID</span>
              <p className="font-mono text-sm text-foreground">{connection.account_id || "-"}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">Role ARN</span>
              <p className="font-mono text-sm text-foreground break-all">{connection.role_arn || "-"}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">Region</span>
              <p className="font-mono text-sm text-foreground">{connection.region}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">Last synced</span>
              <p className="text-sm text-foreground">
                {connection.last_fetch_at ? new Date(connection.last_fetch_at).toLocaleString() : "Never"}
              </p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">Created</span>
              <p className="text-sm text-foreground">{new Date(connection.created_at).toLocaleDateString()}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground">S3 CUR Bucket</span>
              <p className="font-mono text-sm text-foreground">{connection.s3_cur_bucket || "-"}</p>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-white/8 rounded-xl p-4 space-y-4">
          <h3 className="text-sm font-semibold text-foreground">Manual Fetch</h3>
          <div className="flex flex-wrap items-center gap-3">
            <DateRangePicker value={fetchRange} onChange={setFetchRange} />
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useCur}
                onChange={(e) => setUseCur(e.target.checked)}
                className="size-4 rounded border-white/20 accent-cyan"
              />
              <span className="text-sm text-muted-foreground">Use CUR</span>
            </label>
            <button
              onClick={handleFetch}
              disabled={fetching}
              className="flex items-center gap-2 h-8 px-3 rounded-lg bg-cyan text-space text-sm font-semibold hover:bg-cyan/90 transition-all duration-100 disabled:opacity-50"
            >
              {fetching ? <Loader2 className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}
              Fetch now
            </button>
          </div>
          {fetchStep && (
            <div className="text-sm text-muted-foreground flex items-center gap-2">
              {fetching && <Loader2 className="size-3.5 animate-spin text-cyan" />}
              {fetchStep}
            </div>
          )}
        </div>

        <div className="bg-surface border border-white/8 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-white/8">
            <h3 className="text-sm font-semibold text-foreground">Fetch History</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/8">
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground font-medium">Date range</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground font-medium">Rows fetched</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground font-medium">Rows processed</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground font-medium">Duration</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-6 text-center text-sm text-muted-foreground">
                      No fetch history yet
                    </td>
                  </tr>
                ) : (
                  history.slice(0, 6).map((h, i) => (
                    <tr
                      key={h.id}
                      className="border-b border-white/8 last:border-b-0"
                      style={{
                        animation: reduced ? "none" : `fade-up 250ms ${i * 40}ms var(--ease-out-expo) both`,
                      }}
                    >
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                        {h.start_date ? new Date(h.start_date).toLocaleDateString() : "-"} &ndash;{" "}
                        {h.end_date ? new Date(h.end_date).toLocaleDateString() : "-"}
                      </td>
                      <td className="px-4 py-2 font-mono text-xs text-foreground">{h.rows_fetched}</td>
                      <td className="px-4 py-2 font-mono text-xs text-foreground">{h.rows_processed}</td>
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                        {h.duration_seconds ? `${h.duration_seconds.toFixed(1)}s` : "-"}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={cn(
                            "inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium",
                            h.status === "success" && "bg-emerald-500/15 text-emerald-400",
                            h.status === "error" && "bg-ember/15 text-ember",
                            h.status === "running" && "bg-cyan/15 text-cyan",
                            !["success", "error", "running"].includes(h.status) && "bg-muted text-muted-foreground",
                          )}
                        >
                          {h.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="border-t border-white/8 pt-6">
          <button
            onClick={() => setDeleteModal(true)}
            className="flex items-center gap-2 text-sm text-ember hover:text-ember/80 transition-colors duration-100"
          >
            <Trash2 className="size-4" />
            Delete connection
          </button>
        </div>

        {deleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-space/80 backdrop-blur-sm" onClick={() => setDeleteModal(false)} />
            <div className="relative bg-surface border border-white/8 rounded-2xl w-full max-w-sm mx-4 p-6" style={{ animation: "fade-up 200ms var(--ease-out-expo)" }}>
              <h3 className="text-base font-semibold text-foreground mb-2">Delete connection</h3>
              <p className="text-sm text-muted-foreground mb-5">
                This will remove the connection and stop all syncs. Your existing cost data will be preserved.
              </p>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setDeleteModal(false)}
                  className="h-8 px-3 rounded-lg border border-white/8 text-sm text-muted-foreground hover:bg-white/5 transition-colors duration-100"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  className="h-8 px-3 rounded-lg bg-destructive text-white text-sm font-medium hover:bg-destructive/90 transition-all duration-100"
                >
                  Delete connection
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
