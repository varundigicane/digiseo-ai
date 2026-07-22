"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, setSession } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const fd = new FormData(e.currentTarget);
    try {
      const res = await api<{ access_token: string; org_id: string; workspace_id?: string }>(
        "/auth/signup",
        {
          method: "POST",
          session: null,
          body: JSON.stringify({
            email: fd.get("email"),
            password: fd.get("password"),
            full_name: fd.get("full_name"),
            organization_name: fd.get("organization_name"),
            workspace_name: fd.get("workspace_name") || "Default",
          }),
        },
      );
      setSession({
        access_token: res.access_token,
        org_id: res.org_id,
        workspace_id: res.workspace_id,
      });
      router.push("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <Link href="/" className="font-display mb-8 text-2xl text-accent">
        DigiSEO AI
      </Link>
      <h1 className="font-display text-3xl">Create your workspace</h1>
      <p className="mt-2 text-sm text-muted">Start on Starter with 500 AI credits.</p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        {[
          ["full_name", "Full name", "text"],
          ["email", "Work email", "email"],
          ["password", "Password", "password"],
          ["organization_name", "Company / brand", "text"],
          ["workspace_name", "Workspace name", "text"],
        ].map(([name, label, type]) => (
          <label key={name} className="block text-sm">
            <span className="text-muted">{label}</span>
            <input
              name={name}
              type={type}
              required={name !== "workspace_name"}
              minLength={name === "password" ? 8 : undefined}
              className="mt-1 w-full border border-[var(--line)] bg-elevated px-3 py-2 outline-none focus:border-accent/50"
            />
          </label>
        ))}
        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-accent py-3 font-semibold text-[#04140e] disabled:opacity-60"
        >
          {loading ? "Creating…" : "Create account"}
        </button>
      </form>
      <p className="mt-6 text-sm text-muted">
        Already have an account?{" "}
        <Link href="/login" className="text-accent">
          Sign in
        </Link>
      </p>
    </main>
  );
}
