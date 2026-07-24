"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function WorkflowsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/app/playbook");
  }, [router]);
  return <p className="text-sm text-muted">Workflows renamed to Growth Playbook…</p>;
}
