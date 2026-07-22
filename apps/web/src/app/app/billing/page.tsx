"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function BillingPage() {
  const [sub, setSub] = useState<{
    tier: string;
    credits_balance: number;
    status: string;
    limits: Record<string, unknown>;
  } | null>(null);
  const [msg, setMsg] = useState("");

  function refresh() {
    api<typeof sub>("/billing/subscription").then(setSub);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function upgrade(tier: string) {
    const res = await api<{ mode: string; message?: string; checkout_url?: string }>(
      "/billing/checkout",
      {
        method: "POST",
        body: JSON.stringify({ tier }),
      },
    );
    if (res.checkout_url) {
      window.location.href = res.checkout_url;
      return;
    }
    setMsg(res.message || `Upgraded to ${tier}`);
    refresh();
  }

  async function buyCredits() {
    const res = await api<{ balance: number }>("/billing/credits/purchase", {
      method: "POST",
      body: JSON.stringify({ credits: 500 }),
    });
    setMsg(`Added 500 credits. Balance: ${res.balance}`);
    refresh();
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Billing</h1>
      <p className="mt-2 text-muted">Subscriptions, AI credits, and plan limits.</p>
      {sub && (
        <div className="mt-8 border border-[var(--line)] bg-elevated/50 p-5">
          <div className="text-sm text-muted">Current plan</div>
          <div className="mt-1 font-display text-2xl capitalize">{sub.tier}</div>
          <div className="mt-2 text-sm">
            {sub.credits_balance} credits · status {sub.status}
          </div>
        </div>
      )}
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          { tier: "starter", price: 49 },
          { tier: "professional", price: 149 },
          { tier: "business", price: 399 },
        ].map((p) => (
          <button
            key={p.tier}
            type="button"
            onClick={() => upgrade(p.tier)}
            className="border border-[var(--line)] p-5 text-left hover:border-accent/40"
          >
            <div className="capitalize">{p.tier}</div>
            <div className="mt-2 font-display text-3xl">${p.price}</div>
            <div className="mt-2 text-xs text-accent">Select plan</div>
          </button>
        ))}
      </div>
      <button type="button" onClick={buyCredits} className="mt-6 text-sm text-accent">
        Buy 500 credit pack
      </button>
      {msg && <p className="mt-4 text-sm text-muted">{msg}</p>}
    </div>
  );
}
