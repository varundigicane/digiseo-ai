"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { api, getSession, setSession } from "@/lib/api";

type Competitor = { id: string; name: string; domain: string };

const CHECKLIST = [
  "Initial website + funnel audit",
  "Technical SEO audit",
  "Keyword research",
  "Competitor analysis",
  "Buyer persona & journey mapping",
];

export default function StrategyPage() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [status, setStatus] = useState("");
  const [persona, setPersona] = useState<Record<string, unknown> | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api<{ id: string }[]>("/workspaces").then((ws) => {
      if (ws[0]) {
        setWorkspaceId(ws[0].id);
        const session = getSession();
        if (session) setSession({ ...session, workspace_id: ws[0].id });
      }
    });
  }, []);

  useEffect(() => {
    if (!workspaceId) return;
    api<Competitor[]>(`/competitors?workspace_id=${workspaceId}`)
      .then(setCompetitors)
      .catch(() => setCompetitors([]));
  }, [workspaceId]);

  async function connectSite(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!workspaceId) return;
    setStatus("Working…");
    const fd = new FormData(e.currentTarget);
    try {
      const site = await api<{ id: string; domain: string }>("/sites", {
        method: "POST",
        body: JSON.stringify({ url: fd.get("url"), workspace_id: workspaceId }),
      });
      const crawl = await api<{ status: string; pages_crawled: number }>(
        `/crawl/${site.id}/start`,
        { method: "POST" },
      );
      localStorage.setItem("digiseo_active_site", site.id);
      await api("/integrations/connect", {
        method: "POST",
        body: JSON.stringify({
          provider: "gsc",
          workspace_id: workspaceId,
          meta: { site_id: site.id },
        }),
      });
      setStatus(
        `Site ${site.domain}: crawl ${crawl.status} (${crawl.pages_crawled} pages). GSC mock connected.`,
      );
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Failed");
    }
  }

  async function runKeywords() {
    const session = getSession();
    const siteId = localStorage.getItem("digiseo_active_site");
    if (!session?.workspace_id) return;
    setMsg("");
    try {
      const run = await api<{ output_payload: Record<string, unknown> }>("/agents/run", {
        method: "POST",
        body: JSON.stringify({
          agent: "keyword",
          workspace_id: session.workspace_id,
          site_id: siteId,
          goal: "Keyword research for strategy",
        }),
      });
      setPersona({ keywords: run.output_payload });
      setMsg("Keyword research complete");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  async function buildPersona() {
    const session = getSession();
    if (!session?.workspace_id) return;
    try {
      const run = await api<{ output_payload: Record<string, unknown> }>("/agents/run", {
        method: "POST",
        body: JSON.stringify({
          agent: "content",
          workspace_id: session.workspace_id,
          site_id: localStorage.getItem("digiseo_active_site"),
          goal: "Buyer persona and journey map",
          input_payload: {
            content_type: "case_study",
            topic: "Buyer persona & journey for our ICP",
            keywords: ["buyer persona", "customer journey"],
          },
        }),
      });
      setPersona(run.output_payload);
      setMsg("Persona draft generated — refine in Content Studio");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  async function addCompetitor(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!workspaceId) return;
    const fd = new FormData(e.currentTarget);
    try {
      await api("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ tier: "professional" }),
      });
      await api("/competitors", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          name: fd.get("name"),
          domain: fd.get("domain"),
        }),
      });
      setCompetitors(await api(`/competitors?workspace_id=${workspaceId}`));
      e.currentTarget.reset();
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Competitor requires Professional+");
    }
  }

  async function scanCompetitor(id: string) {
    try {
      await api(`/competitors/${id}/scan`, { method: "POST" });
      setMsg("Competitor scan complete");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Strategy & Audit</h1>
      <p className="mt-2 text-muted">
        First step in the growth hierarchy: website + funnel audit, technical SEO, keywords,
        competitors, and persona mapping.
      </p>

      <ol className="mt-6 list-decimal space-y-1 pl-5 text-sm text-muted">
        {CHECKLIST.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ol>

      <section className="mt-10 max-w-xl">
        <h2 className="font-display text-xl">1. Connect site & crawl</h2>
        <form onSubmit={connectSite} className="mt-4 space-y-3">
          <input
            name="url"
            required
            placeholder="https://example.com"
            className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={!workspaceId}
            className="bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
          >
            Connect & crawl
          </button>
        </form>
        {status && <p className="mt-3 text-sm text-accent">{status}</p>}
        <p className="mt-2 text-xs text-muted">
          Or use legacy{" "}
          <Link href="/app/onboarding" className="text-accent">
            Onboarding
          </Link>
          .
        </p>
      </section>

      <section className="mt-10">
        <h2 className="font-display text-xl">2. Keyword research</h2>
        <button
          type="button"
          onClick={runKeywords}
          className="mt-3 border border-[var(--line)] px-4 py-2 text-sm hover:border-accent/40"
        >
          Run keyword clustering
        </button>
      </section>

      <section className="mt-10 max-w-xl">
        <h2 className="font-display text-xl">3. Competitor analysis</h2>
        <p className="mt-1 text-xs text-muted">Capability inside Strategy — not a separate product.</p>
        <form onSubmit={addCompetitor} className="mt-3 flex flex-wrap gap-2">
          <input name="name" required placeholder="Name" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm" />
          <input name="domain" required placeholder="domain.com" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm" />
          <button type="submit" className="bg-accent px-3 py-2 text-sm font-semibold text-[#04140e]">
            Add
          </button>
        </form>
        <ul className="mt-4 space-y-2">
          {competitors.map((c) => (
            <li key={c.id} className="flex justify-between border border-[var(--line)] px-3 py-2 text-sm">
              <span>
                {c.name} · {c.domain}
              </span>
              <button type="button" className="text-accent" onClick={() => scanCompetitor(c.id)}>
                Scan
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10">
        <h2 className="font-display text-xl">4. Buyer persona & journey</h2>
        <button
          type="button"
          onClick={buildPersona}
          className="mt-3 border border-[var(--line)] px-4 py-2 text-sm hover:border-accent/40"
        >
          Generate persona draft
        </button>
      </section>

      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      {persona && (
        <pre className="mt-6 max-h-80 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(persona, null, 2)}
        </pre>
      )}

      <div className="mt-10 flex flex-wrap gap-3 text-sm">
        <Link href="/app/ai-seo" className="text-accent">
          Next: AI SEO →
        </Link>
        <Link href="/app/on-page" className="text-accent">
          On-Page SEO →
        </Link>
      </div>
    </div>
  );
}
