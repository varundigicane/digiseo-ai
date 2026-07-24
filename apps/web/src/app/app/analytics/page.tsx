"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AnalyticsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/app/reporting");
  }, [router]);
  return <p className="text-sm text-muted">Analytics moved to Reporting & Support…</p>;
}
