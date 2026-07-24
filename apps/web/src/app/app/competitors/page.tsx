"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function CompetitorsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/app/strategy");
  }, [router]);
  return <p className="text-sm text-muted">Competitors moved under Strategy & Audit…</p>;
}
