"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Competitor = { id: string; name: string; domain: string };
type Event = { id: string; event_type: string; title: string; payload: Record<string, unknown> };

export default function CompetitorsPage() {
  const [list, setList] = useState<Competitor[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [msg, setMsg] = useState("");

  async function ensurePlan() {
    await api("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ tier: "professional" }),
    });
  }

  async function refresh() {
    const session = getSession();
    if (!session?.workspace_id) return;
    try {
      await ensurePlan();
      setList(await api(`/competitors?workspace_id=${session.workspace_id}`));
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onAdd(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const session = getSession();
    if (!session?.workspace_id) return;
    const fd = new FormData(e.currentTarget);
    await ensurePlan();
    await api("/competitors", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: session.workspace_id,
        name: fd.get("name"),
        domain: fd.get("domain"),
      }),
    });
    refresh();
    e.currentTarget.reset();
  }

  async function scan(id: string) {
    const out = await api<Record<string, unknown>>(`/competitors/${id}/scan`, { method: "POST" });
    setMsg(`Scan complete: ${JSON.stringify(out.events || out).slice(0, 120)}…`);
    setEvents(await api(`/competitors/${id}/events`));
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Competitor intelligence</h1>
      <p className="mt-2 text-muted">Track blogs, keywords, ads, social, and AI Overview mentions.</p>
      <form onSubmit={onAdd} className="mt-8 flex max-w-xl flex-wrap gap-2">
        <input name="name" required placeholder="Name" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm" />
        <input name="domain" required placeholder="domain.com" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm" />
        <button type="submit" className="bg-accent px-4 py-2 font-semibold text-[#04140e]">
          Add
        </button>
      </form>
      {msg && <p className="mt-3 text-sm text-muted">{msg}</p>}
      <ul className="mt-6 space-y-2">
        {list.map((c) => (
          <li key={c.id} className="flex items-center justify-between border border-[var(--line)] px-4 py-3 text-sm">
            <span>
              {c.name} · {c.domain}
            </span>
            <button type="button" className="text-accent" onClick={() => scan(c.id)}>
              Scan
            </button>
          </li>
        ))}
      </ul>
      {events.length > 0 && (
        <ul className="mt-8 space-y-2 text-sm">
          {events.map((ev) => (
            <li key={ev.id} className="border border-[var(--line)] px-3 py-2">
              <span className="text-accent">{ev.event_type}</span> — {ev.title}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
