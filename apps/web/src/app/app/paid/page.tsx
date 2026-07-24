"use client";

import { FormEvent, useState } from "react";
import { api, getSession } from "@/lib/api";

type Tab = "google" | "meta" | "linkedin";

const GOOGLE_ITEMS = [
  "Google Ads Campaign Setup",
  "Campaigns / Ad Groups",
  "Ad Copywriting",
  "Conversion Tracking",
  "Remarketing Ads",
  "Display / Shopping Ads",
  "Performance Max Campaigns",
  "A/B Ad Testing",
];

export default function PaidMediaPage() {
  const [tab, setTab] = useState<Tab>("google");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [campaigns, setCampaigns] = useState<Record<string, unknown>[]>([]);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function optimize(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const session = getSession();
    if (!session?.workspace_id) return;
    setBusy(true);
    setMsg("");
    const fd = new FormData(e.currentTarget);
    try {
      await api("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ tier: "business" }),
      });
      const out = await api<Record<string, unknown>>("/ppc/optimize", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          platform: tab,
          name: fd.get("name") || `${tab} campaign`,
          budget_daily: Number(fd.get("budget") || 50),
          keywords: String(fd.get("keywords") || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          landing_page_url: fd.get("landing") || undefined,
          goal: fd.get("goal") || "Lead gen",
        }),
      });
      setResult(out);
      setCampaigns(
        await api(`/ppc/campaigns?workspace_id=${session.workspace_id}`),
      );
      setMsg(`${tab} campaign draft created`);
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Paid Media requires Business+");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Paid Media</h1>
      <p className="mt-2 text-muted">
        Google Ads and Meta Ads as tabs on one module (not separate products). Drafts only until Ads
        APIs are connected.
      </p>

      <div className="mt-6 flex gap-2">
        {(["google", "meta", "linkedin"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm capitalize ${
              tab === t ? "bg-accent/15 text-accent" : "border border-[var(--line)] text-muted"
            }`}
          >
            {t === "google" ? "Google Ads" : t === "meta" ? "Meta Ads" : "LinkedIn Ads"}
          </button>
        ))}
      </div>

      {tab === "google" && (
        <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
          {GOOGLE_ITEMS.map((i) => (
            <li key={i}>{i}</li>
          ))}
        </ul>
      )}

      <form onSubmit={optimize} className="mt-8 max-w-lg space-y-3">
        <input
          name="name"
          placeholder="Campaign name"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="goal"
          placeholder="Goal"
          defaultValue="Lead gen for DigiSEO AI"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="keywords"
          placeholder="Keywords (comma-separated)"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="budget"
          type="number"
          placeholder="Daily budget"
          defaultValue={50}
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="landing"
          placeholder="Landing page URL"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={busy}
          className="bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
        >
          {busy ? "Creating…" : `Create ${tab} draft`}
        </button>
      </form>
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      {campaigns.length > 0 && (
        <ul className="mt-6 space-y-2 text-sm">
          {campaigns.map((c, i) => (
            <li key={String(c.id ?? i)} className="border border-[var(--line)] px-3 py-2">
              {String(c.name ?? c.platform ?? "campaign")} · {String(c.platform ?? "")}
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
