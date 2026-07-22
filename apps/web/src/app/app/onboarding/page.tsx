"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, getSession, setSession } from "@/lib/api";

export default function OnboardingPage() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api<{ id: string }[]>("/workspaces").then((ws) => {
      if (ws[0]) {
        setWorkspaceId(ws[0].id);
        const session = getSession();
        if (session) setSession({ ...session, workspace_id: ws[0].id });
      }
    });
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!workspaceId) return;
    setLoading(true);
    setStatus("");
    const fd = new FormData(e.currentTarget);
    try {
      const site = await api<{ id: string; domain: string }>("/sites", {
        method: "POST",
        body: JSON.stringify({ url: fd.get("url"), workspace_id: workspaceId }),
      });
      setStatus(`Site ${site.domain} created. Starting crawl…`);
      const crawl = await api<{ status: string; pages_crawled: number }>(
        `/crawl/${site.id}/start`,
        { method: "POST" },
      );
      setStatus(
        `Crawl ${crawl.status}: ${crawl.pages_crawled} pages indexed. Connect GSC next (optional).`,
      );
      await api("/integrations/connect", {
        method: "POST",
        body: JSON.stringify({
          provider: "gsc",
          workspace_id: workspaceId,
          meta: { site_id: site.id },
        }),
      });
      setStatus((s) => `${s} GSC connected (mock).`);
      localStorage.setItem("digiseo_active_site", site.id);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="font-display text-3xl">Onboarding</h1>
      <p className="mt-2 text-muted">
        Connect your website, crawl pages, and link Google Search Console.
      </p>
      <ol className="mt-6 list-decimal space-y-2 pl-5 text-sm text-muted">
        <li>Add your site URL</li>
        <li>We crawl robots.txt, sitemap, and on-page signals</li>
        <li>Chunks are indexed in Qdrant for AEO retrieval</li>
        <li>GSC connects for keyword research</li>
      </ol>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <label className="block text-sm">
          <span className="text-muted">Website URL</span>
          <input
            name="url"
            required
            placeholder="https://example.com"
            className="mt-1 w-full border border-[var(--line)] bg-elevated px-3 py-2 outline-none focus:border-accent/50"
          />
        </label>
        <button
          type="submit"
          disabled={loading || !workspaceId}
          className="bg-accent px-5 py-2 font-semibold text-[#04140e] disabled:opacity-60"
        >
          {loading ? "Working…" : "Connect & crawl"}
        </button>
      </form>
      {status && <p className="mt-4 text-sm text-accent">{status}</p>}
    </div>
  );
}
