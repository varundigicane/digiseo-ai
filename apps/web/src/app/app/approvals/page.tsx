"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type CR = {
  id: string;
  agent: string;
  change_type: string;
  title: string;
  status: string;
  payload: Record<string, unknown>;
};

export default function ApprovalsPage() {
  const [items, setItems] = useState<CR[]>([]);

  async function refresh() {
    setItems(await api<CR[]>("/change-requests?status_filter=proposed"));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function review(id: string, status: "approved" | "rejected") {
    await api(`/change-requests/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ status }),
    });
    refresh();
  }

  return (
    <div>
      <h1 className="font-display text-3xl">Approvals</h1>
      <p className="mt-2 text-muted">
        Human-in-the-loop gate for meta, schema, CMS, and social changes.
      </p>
      <ul className="mt-8 space-y-3">
        {items.length === 0 && <li className="text-sm text-muted">No pending proposals.</li>}
        {items.map((cr) => (
          <li key={cr.id} className="border border-[var(--line)] bg-elevated/40 p-4 text-sm">
            <div className="text-xs uppercase text-muted">
              {cr.agent} · {cr.change_type}
            </div>
            <div className="mt-1 font-medium">{cr.title}</div>
            <pre className="mt-2 max-h-32 overflow-auto text-xs text-muted">
              {JSON.stringify(cr.payload, null, 2)}
            </pre>
            <div className="mt-3 flex gap-3">
              <button type="button" className="text-accent" onClick={() => review(cr.id, "approved")}>
                Approve
              </button>
              <button
                type="button"
                className="text-[var(--danger)]"
                onClick={() => review(cr.id, "rejected")}
              >
                Reject
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
