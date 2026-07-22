"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, unknown> | null>(null);
  const [integrations, setIntegrations] = useState<{ provider: string; status: string }[]>([]);
  const [msg, setMsg] = useState("");
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    api<{ provider: string; status: string }[]>("/integrations").then(setIntegrations);
    api("/billing/checkout", { method: "POST", body: JSON.stringify({ tier: "enterprise" }) })
      .then(() => api<Record<string, unknown>>("/enterprise/settings"))
      .then(setSettings)
      .catch(() =>
        api<Record<string, unknown>>("/enterprise/settings")
          .then(setSettings)
          .catch((e) => setMsg(e instanceof Error ? e.message : "Failed")),
      );
  }, []);

  async function connect(provider: string) {
    await api("/integrations/connect", {
      method: "POST",
      body: JSON.stringify({ provider }),
    });
    setIntegrations(await api("/integrations"));
    setMsg(`Connected ${provider}`);
  }

  async function createKey() {
    await api("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ tier: "business" }),
    });
    const res = await api<{ api_key: string }>("/enterprise/api-keys", { method: "POST" });
    setApiKey(res.api_key);
  }

  async function saveWhiteLabel() {
    await api("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ tier: "enterprise" }),
    });
    await api("/enterprise/white-label", {
      method: "PUT",
      body: JSON.stringify({
        enabled: true,
        custom_domain: "seo.youragency.com",
        brand_logo_url: "/logo.svg",
        brand_primary_color: "#3dffa8",
      }),
    });
    setSettings(await api<Record<string, unknown>>("/enterprise/settings"));
    setMsg("White-label settings saved");
  }

  async function enableSSO() {
    await api("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ tier: "enterprise" }),
    });
    await api("/enterprise/sso", {
      method: "PUT",
      body: JSON.stringify({
        enabled: true,
        metadata_url: "https://idp.example.com/metadata",
        entity_id: "digiseo-ai",
      }),
    });
    setMsg("SSO configured (stub)");
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Settings</h1>
      <p className="mt-2 text-muted">Integrations, white-label, API access, and SSO.</p>

      <h2 className="mt-8 font-display text-xl">Integrations</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {["gsc", "ga4", "gbp", "wordpress", "shopify", "ahrefs", "hubspot"].map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => connect(p)}
            className="border border-[var(--line)] px-3 py-1.5 text-sm capitalize"
          >
            {p}
          </button>
        ))}
      </div>
      <ul className="mt-4 text-sm text-muted">
        {integrations.map((i) => (
          <li key={i.provider}>
            {i.provider}: {i.status}
          </li>
        ))}
      </ul>

      <h2 className="mt-10 font-display text-xl">Enterprise</h2>
      <div className="mt-3 flex flex-wrap gap-3">
        <button type="button" onClick={createKey} className="border border-[var(--line)] px-3 py-2 text-sm">
          Create API key
        </button>
        <button type="button" onClick={saveWhiteLabel} className="border border-[var(--line)] px-3 py-2 text-sm">
          Enable white-label
        </button>
        <button type="button" onClick={enableSSO} className="border border-[var(--line)] px-3 py-2 text-sm">
          Configure SSO
        </button>
        <button
          type="button"
          className="border border-[var(--line)] px-3 py-2 text-sm"
          onClick={async () => {
            await api("/billing/checkout", {
              method: "POST",
              body: JSON.stringify({ tier: "business" }),
            });
            await api("/enterprise/auto-apply?enabled=true", { method: "POST" });
            setMsg("Auto-apply enabled for approved changes");
          }}
        >
          Enable auto-apply
        </button>
      </div>
      {apiKey && (
        <p className="mt-4 break-all rounded border border-[var(--line)] bg-elevated/50 p-3 text-xs">
          {apiKey}
        </p>
      )}
      {settings && (
        <pre className="mt-6 overflow-auto border border-[var(--line)] p-4 text-xs">
          {JSON.stringify(settings, null, 2)}
        </pre>
      )}
      {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
    </div>
  );
}
