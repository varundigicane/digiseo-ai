"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, getSession } from "@/lib/api";

type Post = {
  id: string;
  platform: string;
  body: string;
  hashtags: string[];
  script?: string;
  status: string;
};

export default function SocialPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  async function ensurePlan() {
    await api("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ tier: "professional" }),
    });
  }

  async function refresh() {
    const session = getSession();
    try {
      const list = await api<Post[]>(`/social/posts?workspace_id=${session?.workspace_id}`);
      setPosts(list);
    } catch {
      setPosts([]);
    }
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
      await ensurePlan();
      await api("/social/accounts", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          platform: fd.get("platform"),
          handle: "@digiseo",
        }),
      }).catch(() => null);
      const post = await api<Post>("/social/generate", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: session.workspace_id,
          platform: fd.get("platform"),
          topic: fd.get("topic"),
          tone: "engaging",
        }),
      });
      setPosts((p) => [post, ...p]);
      setMsg("Draft created — schedule or publish when ready.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  async function publish(id: string) {
    await api(`/social/posts/${id}/publish`, { method: "POST" });
    refresh();
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Social media</h1>
      <p className="mt-2 text-muted">
        LinkedIn, X, Facebook, Instagram, Threads, YouTube & TikTok scripts.
      </p>
      <form onSubmit={onGenerate} className="mt-8 flex max-w-xl flex-col gap-3">
        <select name="platform" className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm">
          {["linkedin", "x", "facebook", "instagram", "threads", "youtube", "tiktok"].map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <input
          name="topic"
          required
          placeholder="Post topic"
          className="border border-[var(--line)] bg-elevated px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-fit bg-accent px-4 py-2 font-semibold text-[#04140e]"
        >
          {loading ? "Generating…" : "Generate post"}
        </button>
      </form>
      {msg && <p className="mt-3 text-sm text-accent">{msg}</p>}
      <ul className="mt-8 space-y-4">
        {posts.map((p) => (
          <li key={p.id} className="border border-[var(--line)] bg-elevated/40 p-4 text-sm">
            <div className="text-xs uppercase text-muted">
              {p.platform} · {p.status}
            </div>
            <pre className="mt-2 whitespace-pre-wrap font-sans">{p.body}</pre>
            {p.script && (
              <div className="mt-3 border-t border-[var(--line)] pt-3 text-muted">
                Script: {p.script}
              </div>
            )}
            {p.status !== "published" && (
              <button
                type="button"
                className="mt-3 text-accent"
                onClick={() => publish(p.id)}
              >
                Publish now
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
