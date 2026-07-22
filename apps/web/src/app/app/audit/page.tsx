"use client";

import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Site = { id: string; domain: string; seo_score?: number; aeo_score?: number };
type Issue = {
  id: string;
  severity: string;
  title: string;
  recommendation: string;
  category: string;
};

export default function AuditPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [issues, setIssues] = useState<Issue[]>([]);
  const [output, setOutput] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState("");

  useEffect(() => {
    api<Site[]>("/sites").then((list) => {
      setSites(list);
      const saved = localStorage.getItem("digiseo_active_site");
      setSiteId(saved && list.some((s) => s.id === saved) ? saved : list[0]?.id || "");
    });
  }, []);

  async function run(agent: "seo" | "aeo" | "keyword") {
    const session = getSession();
    if (!siteId || !session?.workspace_id) return;
    setBusy(agent);
    try {
      const run = await api<{ output_payload: Record<string, unknown> }>("/agents/run", {
        method: "POST",
        body: JSON.stringify({
          agent,
          workspace_id: session.workspace_id,
          site_id: siteId,
          goal: `${agent} audit`,
        }),
      });
      setOutput(run.output_payload);
      if (agent === "seo") {
        const iss = await api<Issue[]>(`/crawl/${siteId}/issues`);
        setIssues(iss);
      }
      const refreshed = await api<Site[]>("/sites");
      setSites(refreshed);
    } catch (err) {
      setOutput({ error: err instanceof Error ? err.message : "Failed" });
    } finally {
      setBusy("");
    }
  }

  const site = sites.find((s) => s.id === siteId);

  return (
    <div>
      <h1 className="font-display text-3xl">SEO & AEO</h1>
      <p className="mt-2 text-muted">Technical audits, answer-engine readiness, and keyword clusters.</p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
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
        {(["seo", "aeo", "keyword"] as const).map((a) => (
          <button
            key={a}
            type="button"
            disabled={!siteId || !!busy}
            onClick={() => run(a)}
            className="border border-[var(--line)] px-3 py-2 text-sm capitalize hover:border-accent/40 disabled:opacity-50"
          >
            {busy === a ? "Running…" : `Run ${a}`}
          </button>
        ))}
      </div>

      {site && (
        <div className="mt-6 flex gap-6 text-sm">
          <div>
            SEO score: <span className="text-accent">{site.seo_score ?? "—"}</span>
          </div>
          <div>
            AEO score: <span className="text-accent">{site.aeo_score ?? "—"}</span>
          </div>
        </div>
      )}

      {output && (
        <pre className="mt-6 max-h-80 overflow-auto border border-[var(--line)] bg-elevated/50 p-4 text-xs">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}

      {issues.length > 0 && (
        <>
          <h2 className="mt-10 font-display text-xl">Issues</h2>
          <ul className="mt-4 space-y-2">
            {issues.slice(0, 30).map((issue) => (
              <li key={issue.id} className="border border-[var(--line)] px-4 py-3 text-sm">
                <div className="flex gap-2">
                  <span className="uppercase text-[var(--warn)]">{issue.severity}</span>
                  <span className="text-muted">{issue.category}</span>
                </div>
                <div className="mt-1 font-medium">{issue.title}</div>
                <div className="mt-1 text-muted">{issue.recommendation}</div>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
