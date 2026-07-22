"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, setSession } from "@/lib/api";

export default function LoginPage() {
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
        "/auth/login",
        {
          method: "POST",
          session: null,
          body: JSON.stringify({
            email: fd.get("email"),
            password: fd.get("password"),
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
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <Link href="/" className="font-display mb-8 text-2xl text-accent">
        DigiSEO AI
      </Link>
      <h1 className="font-display text-3xl">Welcome back</h1>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <label className="block text-sm">
          <span className="text-muted">Email</span>
          <input
            name="email"
            type="email"
            required
            className="mt-1 w-full border border-[var(--line)] bg-elevated px-3 py-2 outline-none focus:border-accent/50"
          />
        </label>
        <label className="block text-sm">
          <span className="text-muted">Password</span>
          <input
            name="password"
            type="password"
            required
            className="mt-1 w-full border border-[var(--line)] bg-elevated px-3 py-2 outline-none focus:border-accent/50"
          />
        </label>
        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-accent py-3 font-semibold text-[#04140e] disabled:opacity-60"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-6 text-sm text-muted">
        New here?{" "}
        <Link href="/signup" className="text-accent">
          Create account
        </Link>
      </p>
    </main>
  );
}
