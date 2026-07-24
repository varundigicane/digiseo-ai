"use client";

import { useState } from "react";
import { api, getSession } from "@/lib/api";

const CRO_ITEMS = [
  "Conversion Optimisation",
  "Funnel Strategy",
  "Landing Page Optimisation",
  "Heatmap & User Behaviour Tracking (partner)",
  "A/B Testing",
  "Exit-Intent & Pop-up Strategy",
];

export default function CroPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    const session = getSession();
    if (!session?.workspace_id) return;
    setBusy(true);
    setMsg("");
    try {
      await api("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ tier: "professional" }),
      });
      const out = await api<Record<string, unknown>>("/growth/cro", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          site_id: localStorage.getItem("digiseo_active_site"),
          offer: "primary conversion",
          goal: "Improve conversion rate",
        }),
      });
      setResult(out);
      setMsg("CRO brief ready");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "CRO requires Professional+");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Conversion Rate Optimisation</h1>
      <p className="mt-2 text-muted">
        Funnel and landing briefs, A/B plans, exit-intent — software recommendations (heatmap tools
        via partner).
      </p>
      <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
        {CRO_ITEMS.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
      <button
        type="button"
        disabled={busy}
        onClick={run}
        className="mt-8 bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
      >
        {busy ? "Generating…" : "Generate CRO brief"}
      </button>
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      {result && (
        <pre className="mt-6 max-h-96 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
