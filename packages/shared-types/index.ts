/** Shared DigiSEO types for the Next.js app */

export type PlanTier = "starter" | "professional" | "business" | "enterprise";

export type Role = "owner" | "admin" | "editor" | "viewer";

export interface AuthSession {
  access_token: string;
  org_id: string;
  workspace_id?: string | null;
}

export interface Subscription {
  tier: PlanTier;
  status: string;
  credits_balance: number;
  auto_apply_enabled: boolean;
  limits: Record<string, unknown>;
}

export interface Site {
  id: string;
  workspace_id: string;
  organization_id: string;
  url: string;
  domain: string;
  seo_score?: number | null;
  aeo_score?: number | null;
  last_crawled_at?: string | null;
}

export interface AgentRun {
  id: string;
  agent: string;
  goal: string;
  status: string;
  credits_used: number;
  output_payload: Record<string, unknown>;
  error?: string | null;
  created_at: string;
}

export interface Issue {
  id: string;
  category: string;
  severity: string;
  code: string;
  title: string;
  description: string;
  recommendation: string;
  resolved: boolean;
}

export interface ContentPiece {
  id: string;
  content_type: string;
  title: string;
  body_markdown: string;
  status: string;
  target_keywords: string[];
  meta_title?: string | null;
  meta_description?: string | null;
}

export const PLAN_PRICES = {
  starter: 49,
  professional: 149,
  business: 399,
} as const;

export const AGENTS = [
  { id: "seo", name: "Website SEO", phase: 1 },
  { id: "aeo", name: "AEO", phase: 1 },
  { id: "content", name: "Content Marketing", phase: 1 },
  { id: "keyword", name: "Keyword Research", phase: 1 },
  { id: "social", name: "Social Media", phase: 2 },
  { id: "competitor", name: "Competitor Intel", phase: 2 },
  { id: "analytics", name: "Analytics", phase: 2 },
  { id: "backlink", name: "Backlink Outreach", phase: 3 },
  { id: "ppc", name: "PPC", phase: 3 },
  { id: "local_seo", name: "Local SEO", phase: 3 },
] as const;
