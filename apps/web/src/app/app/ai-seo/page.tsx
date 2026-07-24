"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Site = { id: string; domain: string; seo_score?: number; aeo_score?: number };

const AI_SEO_ITEMS = [
  "AI Keyword Research & Clustering",
  "AI Content Optimisation (AEO & GEO)",
  "AI Competitor Intelligence",
  "SGE / AI Overview Optimisation",
  "AI SEO Performance Tracking",
];

export default function AiSeoPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [output, setOutput] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState("");

  useEffect(() => {
    api<Site[]>("/sites").then((list) => {
      setSites(list);
      const saved = localStorage.getItem("digiseo_active_site");
      setSiteId(saved && list.some((s) => s.id === saved) ? saved : list[0]?.id || "");
    });
  }, []);

  async function run(agent: "aeo" | "keyword" | "competitor") {
    const session = getSession();
    if (!session?.workspace_id) return;
    setBusy(agent);
    try {
      if (agent === "competitor") {
        await api("/billing/checkout", {
          method: "POST",
          body: JSON.stringify({ tier: "professional" }),
        });
      }
      const runRes = await api<{ output_payload: Record<string, unknown> }>("/agents/run", {
        method: "POST",
        body: JSON.stringify({
          agent,
          workspace_id: session.workspace_id,
          site_id: siteId || undefined,
          goal: `${agent} for AI SEO`,
        }),
      });
      setOutput(runRes.output_payload);
      if (agent === "aeo") {
        const refreshed = await api<Site[]>("/sites");
        setSites(refreshed);
      }
    } catch (err) {
      setOutput({ error: err instanceof Error ? err.message : "Failed" });
    } finally {
      setBusy("");
    }
  }

  const site = sites.find((s) => s.id === siteId);

  return (
    <div>
      <h1 className="font-display text-3xl">AI SEO</h1>
      <p className="mt-2 text-muted">
        Answer engines, GEO, SGE / AI Overviews, clustering, and AI competitor signals.
      </p>
      <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
        {AI_SEO_ITEMS.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <select
          value={siteId}
          onChange={(e) => {
            setSiteId(e.target.value);
            localStorage.setItem("digiseo_active_site", e.target.value);
          }}
          className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        >
          {sites.map((s) => (
            <option key={s.id} value={s.id}>
              {s.domain}
            </option>
          ))}
        </select>
        <button
          type="button"
          disabled={!siteId || !!busy}
          onClick={() => run("aeo")}
          className="border border-[var(--line)] px-3 py-2 text-sm hover:border-accent/40 disabled:opacity-50"
        >
          {busy === "aeo" ? "Running…" : "Run AEO / GEO"}
        </button>
        <button
          type="button"
          disabled={!siteId || !!busy}
          onClick={() => run("keyword")}
          className="border border-[var(--line)] px-3 py-2 text-sm hover:border-accent/40 disabled:opacity-50"
        >
          {busy === "keyword" ? "Running…" : "AI keyword clusters"}
        </button>
        <button
          type="button"
          disabled={!!busy}
          onClick={() => run("competitor")}
          className="border border-[var(--line)] px-3 py-2 text-sm hover:border-accent/40 disabled:opacity-50"
        >
          {busy === "competitor" ? "Running…" : "AI competitor intel"}
        </button>
      </div>

      {site && (
        <div className="mt-6 text-sm">
          AEO score: <span className="text-accent">{site.aeo_score ?? "—"}</span>
        </div>
      )}

      {output && (
        <pre className="mt-6 max-h-96 overflow-auto border border-[var(--line)] bg-elevated/50 p-4 text-xs">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}

      <p className="mt-8 text-sm text-muted">
        Full technical + on-page checklist lives in{" "}
        <Link href="/app/on-page" className="text-accent">
          On-Page SEO
        </Link>
        .
      </p>
    </div>
  );
}
