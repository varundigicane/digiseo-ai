"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, clearSession, getSession } from "@/lib/api";

const NAV = [
  { href: "/app", label: "Overview" },
  { href: "/app/strategy", label: "Strategy & Audit" },
  { href: "/app/ai-seo", label: "AI SEO" },
  { href: "/app/on-page", label: "On-Page SEO" },
  { href: "/app/content", label: "Content Studio" },
  { href: "/app/cro", label: "CRO" },
  { href: "/app/off-page", label: "Off-Page SEO" },
  { href: "/app/local", label: "Local SEO" },
  { href: "/app/paid", label: "Paid Media" },
  { href: "/app/social", label: "Social (SMM)" },
  { href: "/app/email", label: "Email" },
  { href: "/app/reporting", label: "Reporting" },
  { href: "/app/playbook", label: "Growth Playbook" },
  { href: "/app/approvals", label: "Approvals" },
  { href: "/app/billing", label: "Billing" },
  { href: "/app/settings", label: "Settings" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [me, setMe] = useState<{
    user: { full_name: string; email: string };
    subscription: { tier: string; credits_balance: number };
  } | null>(null);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.replace("/login");
      return;
    }
    api<{
      user: { full_name: string; email: string };
      subscription: { tier: string; credits_balance: number };
    }>("/auth/me")
      .then(setMe)
      .catch(() => {
        clearSession();
        router.replace("/login");
      });
  }, [router]);

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl gap-0 md:gap-8">
      <aside className="hidden w-56 shrink-0 border-r border-[var(--line)] px-4 py-6 md:block">
        <Link href="/" className="font-display text-xl text-accent">
          DigiSEO AI
        </Link>
        <nav className="mt-8 max-h-[70vh] space-y-1 overflow-y-auto text-sm">
          {NAV.map((item) => {
            const active =
              item.href === "/app"
                ? pathname === "/app"
                : pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-3 py-2 ${
                  active ? "bg-accent/10 text-accent" : "text-muted hover:text-ink"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        {me && (
          <div className="mt-6 border-t border-[var(--line)] pt-4 text-xs text-muted">
            <div className="text-ink">{me.user.full_name}</div>
            <div className="mt-1 capitalize">{me.subscription.tier}</div>
            <div className="mt-1">{me.subscription.credits_balance} credits</div>
            <button
              type="button"
              className="mt-3 text-accent"
              onClick={() => {
                clearSession();
                router.push("/login");
              }}
            >
              Sign out
            </button>
          </div>
        )}
      </aside>
      <div className="min-w-0 flex-1 px-4 py-6 md:px-2 md:py-8">{children}</div>
    </div>
  );
}
