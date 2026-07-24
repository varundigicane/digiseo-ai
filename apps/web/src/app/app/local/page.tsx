"use client";

import { FormEvent, useState } from "react";
import { api, getSession } from "@/lib/api";

const LOCAL_ITEMS = [
  "GBP Optimisation",
  "Local Citations",
  "Reviews Management",
  "GBP Posts (Per Month)",
  "Local Ranking Tracking",
  "Geo-Grid Tracking",
];

export default function LocalPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
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
      const out = await api<Record<string, unknown>>("/local-seo/optimize", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          business_name: fd.get("business_name"),
          address: fd.get("address") || "",
          phone: fd.get("phone") || "",
          categories: String(fd.get("categories") || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      setResult(out);
      setMsg("Local SEO / GBP plan ready");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Local SEO requires Business+");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Local SEO (GMB)</h1>
      <p className="mt-2 text-muted">
        Google Business Profile optimisation, citations, reviews, posts, and local ranking signals.
      </p>
      <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted">
        {LOCAL_ITEMS.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
      <form onSubmit={optimize} className="mt-8 max-w-md space-y-3">
        <input
          name="business_name"
          required
          placeholder="Business name"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="address"
          placeholder="Address"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="phone"
          placeholder="Phone"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="categories"
          placeholder="Categories (comma-separated)"
          className="w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={busy}
          className="bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
        >
          {busy ? "Optimising…" : "Optimise GBP"}
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
