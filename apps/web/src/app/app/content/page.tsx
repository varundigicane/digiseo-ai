"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Piece = {
  id: string;
  title: string;
  content_type: string;
  body_markdown: string;
  status: string;
  meta_title?: string;
  meta_description?: string;
};

export default function ContentPage() {
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [active, setActive] = useState<Piece | null>(null);
  const [loading, setLoading] = useState(false);
  const [calendar, setCalendar] = useState<{ id: string; title: string; planned_date: string; channel: string }[]>([]);
  const [msg, setMsg] = useState("");

  function refresh() {
    const session = getSession();
    api<Piece[]>(`/content?workspace_id=${session?.workspace_id || ""}`).then(setPieces);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onGenerate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const session = getSession();
    if (!session?.workspace_id) return;
    setLoading(true);
    setMsg("");
    const fd = new FormData(e.currentTarget);
    try {
      const piece = await api<Piece>("/content/generate", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          site_id: localStorage.getItem("digiseo_active_site"),
          content_type: fd.get("content_type"),
          topic: fd.get("topic"),
          keywords: String(fd.get("keywords") || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          tone: "professional",
        }),
      });
      setActive(piece);
      refresh();
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  async function seedCalendar() {
    const session = getSession();
    if (!session?.workspace_id) return;
    try {
      await api(`/billing/checkout`, {
        method: "POST",
        body: JSON.stringify({ tier: "professional" }),
      });
      const items = await api<typeof calendar>(
        `/content/calendar/seed?workspace_id=${session.workspace_id}`,
        { method: "POST" },
      );
      setCalendar(items);
      setMsg("Upgraded to Professional (dev mock) and seeded content calendar.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Calendar requires Professional+");
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Content studio</h1>
      <p className="mt-2 text-muted">Blogs, landing pages, case studies, and calendar planning.</p>

      <form onSubmit={onGenerate} className="mt-8 grid max-w-2xl gap-3">
        <select name="content_type" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm">
          <option value="blog">Blog</option>
          <option value="landing">Landing page</option>
          <option value="case_study">Case study</option>
          <option value="whitepaper">Whitepaper</option>
          <option value="newsletter">Newsletter</option>
          <option value="press_release">Press release</option>
        </select>
        <input
          name="topic"
          required
          placeholder="Topic"
          className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <input
          name="keywords"
          placeholder="Keywords (comma-separated)"
          className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-fit bg-accent px-4 py-2 font-semibold text-[#04140e] disabled:opacity-60"
        >
          {loading ? "Generating…" : "Generate"}
        </button>
      </form>

      <button type="button" onClick={seedCalendar} className="mt-4 text-sm text-accent">
        Seed content calendar (Professional+)
      </button>
      {msg && <p className="mt-2 text-sm text-muted">{msg}</p>}

      {active && (
        <article className="mt-8 border border-[var(--line)] bg-elevated/40 p-5">
          <h2 className="font-display text-2xl">{active.title}</h2>
          <p className="mt-1 text-xs text-muted">
            {active.meta_title} — {active.meta_description}
          </p>
          <pre className="mt-4 whitespace-pre-wrap font-sans text-sm leading-relaxed">
            {active.body_markdown}
          </pre>
        </article>
      )}

      <h2 className="mt-10 font-display text-xl">Drafts</h2>
      <ul className="mt-3 space-y-2 text-sm">
        {pieces.map((p) => (
          <li key={p.id}>
            <button type="button" className="text-left hover:text-accent" onClick={() => setActive(p)}>
              [{p.content_type}] {p.title}
            </button>
          </li>
        ))}
      </ul>

      {calendar.length > 0 && (
        <>
          <h2 className="mt-10 font-display text-xl">Calendar</h2>
          <ul className="mt-3 space-y-2 text-sm text-muted">
            {calendar.map((c) => (
              <li key={c.id}>
                {new Date(c.planned_date).toLocaleDateString()} · {c.channel} · {c.title}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
