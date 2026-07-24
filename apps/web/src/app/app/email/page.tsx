"use client";

import { FormEvent, useState } from "react";
import { api, getSession } from "@/lib/api";

const EMAIL_ITEMS = [
  "Email Campaign Setup",
  "Email Newsletters (Per Month)",
  "Drip / Automation Sequences",
  "List Segmentation",
  "Email A/B Testing",
];

export default function EmailPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function plan(e: FormEvent<HTMLFormElement>) {
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
      const out = await api<Record<string, unknown>>("/growth/email", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          topic: fd.get("topic") || "SEO growth",
          goal: "Email nurture plan",
        }),
      });
      setResult(out);
      setMsg("Email plan ready — connect ESP under Settings to sync");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Email requires Business+");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Email Marketing</h1>
      <p className="mt-2 text-muted">
        Campaigns, newsletters, drips, segments, and A/B plans. ESP send is a later integration.
      </p>
      <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
        {EMAIL_ITEMS.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
      <form onSubmit={plan} className="mt-8 max-w-md space-y-3">
        <input
          name="topic"
          required
          placeholder="Campaign theme"
          defaultValue="SEO growth"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={busy}
          className="bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
        >
          {busy ? "Planning…" : "Generate email plan"}
        </button>
      </form>
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      {result && (
        <pre className="mt-6 max-h-96 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
