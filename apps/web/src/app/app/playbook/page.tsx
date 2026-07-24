"use client";

import { useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

export default function PlaybookPage() {
  const [templates, setTemplates] = useState<
    { id: string; name: string; steps: string[]; description: string }[]
  >([]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        await api("/billing/checkout", {
          method: "POST",
          body: JSON.stringify({ tier: "business" }),
        });
        setTemplates(await api("/workflows/templates"));
      } catch (err) {
        setMsg(err instanceof Error ? err.message : "Business plan required");
      }
    })();
  }, []);

  async function launch(workflow: string) {
    const session = getSession();
    if (!session?.workspace_id) return;
    setBusy(true);
    setMsg("");
    try {
      const run = await api<{ output_payload: Record<string, unknown>; status: string }>(
        "/workflows/launch",
        {
          method: "POST",
          body: JSON.stringify({
            workspace_id: session.workspace_id,
            site_id: localStorage.getItem("digiseo_active_site"),
            workflow,
            goal: "Run DigiSEO growth hierarchy playbook",
          }),
        },
      );
      setResult(run.output_payload);
      setMsg(`Playbook ${run.status}`);
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Growth Playbook</h1>
      <p className="mt-2 text-muted">
        Hierarchy-wise orchestration: Audit → AI SEO / On-Page → Content → CRO → Off-Page / Local →
        Paid / SMM / Email → Reporting.
      </p>
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      <ul className="mt-8 space-y-4">
        {templates.map((t) => (
          <li key={t.id} className="border border-[var(--line)] bg-elevated/40 p-5">
            <div className="font-display text-xl">{t.name}</div>
            <p className="mt-2 text-sm text-muted">{t.description}</p>
            <div className="mt-2 text-xs text-accent">{t.steps.join(" → ")}</div>
            <button
              type="button"
              disabled={busy}
              onClick={() => launch(t.id)}
              className="mt-4 bg-accent px-4 py-2 text-sm font-semibold text-[#04140e] disabled:opacity-60"
            >
              {busy ? "Running…" : "Launch"}
            </button>
          </li>
        ))}
      </ul>
      {result && (
        <pre className="mt-8 max-h-96 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
