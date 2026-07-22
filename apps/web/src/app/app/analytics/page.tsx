"use client";

import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

export default function AnalyticsPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getSession();
    if (!session?.workspace_id) return;
    (async () => {
      try {
        await api("/billing/checkout", {
          method: "POST",
          body: JSON.stringify({ tier: "professional" }),
        });
        await api("/integrations/connect", {
          method: "POST",
          body: JSON.stringify({ provider: "ga4", workspace_id: session.workspace_id }),
        });
        const dash = await api<Record<string, unknown>>(
          `/analytics/dashboard?workspace_id=${session.workspace_id}`,
        );
        setData(dash);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      }
    })();
  }, []);

  const metrics = (data?.metrics || {}) as Record<string, unknown>;

  return (
    <div>
      <h1 className="font-display text-3xl">Analytics</h1>
      <p className="mt-2 text-muted">GA4 + Search Console unified metrics, ROI, and attribution.</p>
      {error && <p className="mt-4 text-sm text-[var(--danger)]">{error}</p>}
      {data && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {["sessions", "organic_sessions", "conversions", "revenue", "roi", "gsc_clicks"].map(
            (key) => (
              <div key={key} className="border border-[var(--line)] bg-elevated/50 p-4">
                <div className="text-xs uppercase tracking-wider text-muted">{key.replaceAll("_", " ")}</div>
                <div className="mt-2 font-display text-2xl">{String(metrics[key] ?? "—")}</div>
              </div>
            ),
          )}
        </div>
      )}
      {data?.summary != null && (
        <p className="mt-6 text-sm text-muted">{String(data.summary)}</p>
      )}
      {metrics.top_channels != null && (
        <pre className="mt-6 border border-[var(--line)] bg-elevated/40 p-4 text-xs">
          {JSON.stringify(metrics.top_channels, null, 2)}
        </pre>
      )}
    </div>
  );
}
