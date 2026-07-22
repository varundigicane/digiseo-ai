const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Session = {
  access_token: string;
  org_id: string;
  workspace_id?: string | null;
};

const SESSION_KEY = "digiseo_session";

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

export function setSession(session: Session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit & { session?: Session | null } = {},
): Promise<T> {
  const session = options.session === undefined ? getSession() : options.session;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (session?.access_token) {
    headers.Authorization = `Bearer ${session.access_token}`;
  }
  if (session?.org_id) {
    headers["X-Org-Id"] = session.org_id;
  }
  if (session?.workspace_id) {
    headers["X-Workspace-Id"] = session.workspace_id;
  }

  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
