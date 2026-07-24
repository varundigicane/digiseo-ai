"use client";

import { useState } from "react";
import { api, getSession } from "@/lib/api";

const OFF_PAGE = [
  "Profile / Directory Creation",
  "Business Listings",
  "Backlink Building",
  "Guest Posting",
  "Email Outreach Campaigns",
  "Competitor Backlink Research",
  "Digital PR & Brand Mentions",
  "Social Bookmarking",
];

export default function OffPagePage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [opps, setOpps] = useState<Record<string, unknown>[]>([]);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function discover() {
    const session = getSession();
    if (!session?.workspace_id) return;
    setBusy(true);
    setMsg("");
    try {
      await api("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ tier: "business" }),
      });
      const out = await api<Record<string, unknown>>(
        `/outreach/discover?workspace_id=${session.workspace_id}&niche=seo`,
        { method: "POST" },
      );
      setResult(out);
      const list = await api<Record<string, unknown>[]>(
        `/outreach/opportunities?workspace_id=${session.workspace_id}`,
      );
      setOpps(list);
      setMsg("Backlink & outreach opportunities discovered");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Off-Page requires Business+");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Off-Page SEO</h1>
      <p className="mt-2 text-muted">
        Directories, listings, backlinks, guest posts, outreach, competitor link research, digital PR.
      </p>
      <ul className="mt-4 grid gap-2 sm:grid-cols-2">
        {OFF_PAGE.map((i) => (
          <li key={i} className="border border-[var(--line)] px-3 py-2 text-sm text-muted">
            {i}
          </li>
        ))}
      </ul>
      <button
        type="button"
        disabled={busy}
        onClick={discover}
        className="mt-8 bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
      >
        {busy ? "Discovering…" : "Discover backlink opportunities"}
      </button>
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      {opps.length > 0 && (
        <ul className="mt-6 space-y-2">
          {opps.slice(0, 20).map((o, idx) => (
            <li key={String(o.id ?? idx)} className="border border-[var(--line)] px-3 py-2 text-sm">
              {String(o.domain ?? o.page_url ?? "opportunity")} · {String(o.outreach_status ?? "")}
            </li>
          ))}
        </ul>
      )}
      {result && (
        <pre className="mt-6 max-h-64 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
