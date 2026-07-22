"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, getSession, setSession } from "@/lib/api";

type Site = {
  id: string;
  domain: string;
  url: string;
  seo_score?: number | null;
  aeo_score?: number | null;
};

export default function AppHome() {
  const [sites, setSites] = useState<Site[]>([]);
  const [me, setMe] = useState<{
    subscription: { tier: string; credits_balance: number; limits: Record<string, unknown> };
  } | null>(null);

  useEffect(() => {
    api<{
      subscription: { tier: string; credits_balance: number; limits: Record<string, unknown> };
    }>("/auth/me").then(setMe);
    api<Site[]>("/sites").then((list) => {
      setSites(list);
      const session = getSession();
      if (session && list[0]) {
        // keep workspace from session
      }
    });
    api<{ id: string }[]>("/workspaces").then((ws) => {
      const session = getSession();
      if (session && ws[0] && !session.workspace_id) {
        setSession({ ...session, workspace_id: ws[0].id });
      }
    });
  }, []);

  return (
    <div>
      <h1 className="font-display text-3xl">Campaign board</h1>
      <p className="mt-2 text-muted">
        Your multi-agent marketing workspace
        {me ? ` · ${me.subscription.credits_balance} credits remaining` : ""}
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {[
          { label: "Sites", value: String(sites.length) },
          {
            label: "Plan",
            value: me?.subscription.tier ?? "—",
          },
          {
            label: "SEO avg",
            value:
              sites.length && sites.some((s) => s.seo_score != null)
                ? String(
                    Math.round(
                      sites.reduce((a, s) => a + (s.seo_score || 0), 0) /
                        sites.filter((s) => s.seo_score != null).length,
                    ),
                  )
                : "—",
          },
        ].map((stat) => (
          <div key={stat.label} className="border border-[var(--line)] bg-elevated/50 p-4">
            <div className="text-xs uppercase tracking-wider text-muted">{stat.label}</div>
            <div className="mt-2 font-display text-2xl capitalize">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link href="/app/onboarding" className="bg-accent px-4 py-2 font-medium text-[#04140e]">
          Connect a site
        </Link>
        <Link
          href="/app/audit"
          className="border border-[var(--line)] px-4 py-2 text-ink hover:border-accent/40"
        >
          Run SEO / AEO
        </Link>
        <Link
          href="/app/content"
          className="border border-[var(--line)] px-4 py-2 text-ink hover:border-accent/40"
        >
          Content studio
        </Link>
      </div>

      <h2 className="mt-12 font-display text-xl">Sites</h2>
      {sites.length === 0 ? (
        <p className="mt-3 text-sm text-muted">No sites yet — start onboarding to crawl your domain.</p>
      ) : (
        <ul className="mt-4 space-y-2">
          {sites.map((s) => (
            <li
              key={s.id}
              className="flex items-center justify-between border border-[var(--line)] bg-elevated/40 px-4 py-3"
            >
              <div>
                <div className="font-medium">{s.domain}</div>
                <div className="text-xs text-muted">{s.url}</div>
              </div>
              <div className="text-right text-sm">
                <div>SEO {s.seo_score ?? "—"}</div>
                <div className="text-muted">AEO {s.aeo_score ?? "—"}</div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
