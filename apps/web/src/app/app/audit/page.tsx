"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AuditRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/app/ai-seo");
  }, [router]);
  return <p className="text-sm text-muted">SEO / AEO split into AI SEO and On-Page…</p>;
}
