"use client";

import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

const SUPPORT = [
  { label: "Report frequency", value: "Weekly + monthly rollup" },
  { label: "Performance dashboard", value: "Live GA4/GSC-style metrics" },
  { label: "Strategy calls", value: "Notes stub for agency AM" },
  { label: "Dedicated account manager", value: "Enterprise white-label (agency supplies AM)" },
  { label: "Support level", value: "In-app + API (Business+)" },
];

export default function ReportingPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [callNote, setCallNote] = useState("");
  const [savedNotes, setSavedNotes] = useState<string[]>([]);

  useEffect(() => {
    const session = getSession();
    if (!session?.workspace_id) return;
    (async () => {
      try {
        await api("/billing/checkout", {
          method: "POST",
          body: JSON.stringify({ tier: "professional" }),
        });
        await api("/integrations/connect", {
          method: "POST",
          body: JSON.stringify({ provider: "ga4", workspace_id: session.workspace_id }),
        });
        const dash = await api<Record<string, unknown>>(
          `/analytics/dashboard?workspace_id=${session.workspace_id}`,
        );
        setData(dash);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      }
    })();
  }, []);

  const metrics = (data?.metrics || {}) as Record<string, unknown>;

  function saveNote() {
    if (!callNote.trim()) return;
    const next = [`${new Date().toISOString().slice(0, 10)}: ${callNote}`, ...savedNotes];
    setSavedNotes(next);
    localStorage.setItem("digiseo_strategy_notes", JSON.stringify(next));
    setCallNote("");
  }

  useEffect(() => {
    try {
      const raw = localStorage.getItem("digiseo_strategy_notes");
      if (raw) setSavedNotes(JSON.parse(raw));
    } catch {
      /* ignore */
    }
  }, []);

  return (
    <div>
      <h1 className="font-display text-3xl">Reporting & Support</h1>
      <p className="mt-2 text-muted">
        End of the delivery hierarchy: performance dashboard, cadence, and strategy notes.
      </p>

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {SUPPORT.map((s) => (
          <div key={s.label} className="border border-[var(--line)] px-4 py-3">
            <div className="text-xs uppercase text-muted">{s.label}</div>
            <div className="mt-1 text-sm">{s.value}</div>
          </div>
        ))}
      </div>

      {error && <p className="mt-4 text-sm text-[var(--danger)]">{error}</p>}
      {data && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {["sessions", "organic_sessions", "conversions", "revenue", "roi", "gsc_clicks"].map(
            (key) => (
              <div key={key} className="border border-[var(--line)] bg-elevated/50 p-4">
                <div className="text-xs uppercase tracking-wider text-muted">
                  {key.replaceAll("_", " ")}
                </div>
                <div className="mt-2 font-display text-2xl">{String(metrics[key] ?? "—")}</div>
              </div>
            ),
          )}
        </div>
      )}

      <section className="mt-10 max-w-xl">
        <h2 className="font-display text-xl">Strategy call notes</h2>
        <textarea
          value={callNote}
          onChange={(e) => setCallNote(e.target.value)}
          rows={3}
          placeholder="Agenda / decisions for next AM call"
          className="mt-3 w-full border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="button"
          onClick={saveNote}
          className="mt-2 border border-[var(--line)] px-3 py-2 text-sm hover:border-accent/40"
        >
          Save note
        </button>
        <ul className="mt-4 space-y-2 text-sm text-muted">
          {savedNotes.map((n) => (
            <li key={n} className="border-b border-[var(--line)] pb-2">
              {n}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
