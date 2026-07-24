"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Site = { id: string; domain: string; seo_score?: number };
type Issue = {
  id: string;
  severity: string;
  title: string;
  recommendation: string;
  category: string;
};

const ON_PAGE = [
  "Meta Tags Optimisation",
  "URL Optimisation",
  "Content Optimisation",
  "Schema / Structured Data",
  "Core Web Vitals Optimisation",
  "Internal Linking Strategy",
  "Voice Optimization",
  "Duplicate Content / AI Content Check",
  "Image Optimisation",
  "FAQ & Featured Snippet Optimisation",
  "E-E-A-T Signals",
];

const CATEGORY_MAP: Record<string, string[]> = {
  meta: ["Meta Tags Optimisation"],
  onpage: ["Content Optimisation", "URL Optimisation"],
  schema: ["Schema / Structured Data", "FAQ & Featured Snippet Optimisation"],
  performance: ["Core Web Vitals Optimisation"],
  links: ["Internal Linking Strategy"],
  images: ["Image Optimisation"],
  eeat: ["E-E-A-T Signals"],
  content: ["Duplicate Content / AI Content Check", "Voice Optimization"],
};

export default function OnPagePage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [issues, setIssues] = useState<Issue[]>([]);
  const [output, setOutput] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Site[]>("/sites").then((list) => {
      setSites(list);
      const saved = localStorage.getItem("digiseo_active_site");
      setSiteId(saved && list.some((s) => s.id === saved) ? saved : list[0]?.id || "");
    });
  }, []);

  async function runSeo() {
    const session = getSession();
    if (!siteId || !session?.workspace_id) return;
    setBusy(true);
    try {
      const run = await api<{ output_payload: Record<string, unknown> }>("/agents/run", {
        method: "POST",
        body: JSON.stringify({
          agent: "seo",
          workspace_id: session.workspace_id,
          site_id: siteId,
          goal: "on-page seo audit",
        }),
      });
      setOutput(run.output_payload);
      setIssues(await api<Issue[]>(`/crawl/${siteId}/issues`));
      setSites(await api<Site[]>("/sites"));
    } catch (err) {
      setOutput({ error: err instanceof Error ? err.message : "Failed" });
    } finally {
      setBusy(false);
    }
  }

  const site = sites.find((s) => s.id === siteId);

  function issuesForChecklist(item: string) {
    return issues.filter((iss) => {
      const cats = Object.entries(CATEGORY_MAP)
        .filter(([, labels]) => labels.includes(item))
        .map(([k]) => k);
      return cats.some((c) => iss.category?.toLowerCase().includes(c) || iss.title.toLowerCase().includes(c));
    });
  }

  return (
    <div>
      <h1 className="font-display text-3xl">On-Page SEO</h1>
      <p className="mt-2 text-muted">
        Checklist mapped to crawl issues and change requests — meta, schema, CWV, links, FAQ, E-E-A-T.
      </p>

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
        <button
          type="button"
          disabled={!siteId || busy}
          onClick={runSeo}
          className="bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
        >
          {busy ? "Auditing…" : "Run on-page audit"}
        </button>
        {site && (
          <span className="text-sm">
            SEO score: <span className="text-accent">{site.seo_score ?? "—"}</span>
          </span>
        )}
      </div>

      <ul className="mt-10 space-y-3">
        {ON_PAGE.map((item) => {
          const related = issuesForChecklist(item);
          return (
            <li key={item} className="border border-[var(--line)] px-4 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{item}</span>
                <span className="text-xs text-muted">
                  {related.length ? `${related.length} issue(s)` : "—"}
                </span>
              </div>
              {related.slice(0, 3).map((iss) => (
                <div key={iss.id} className="mt-2 text-xs text-muted">
                  <span className="uppercase text-[var(--warn)]">{iss.severity}</span> · {iss.title}
                </div>
              ))}
            </li>
          );
        })}
      </ul>

      {output && (
        <pre className="mt-8 max-h-64 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}

      <p className="mt-8 text-sm text-muted">
        Approve meta/schema fixes in{" "}
        <Link href="/app/approvals" className="text-accent">
          Approvals
        </Link>
        .
      </p>
    </div>
  );
}
