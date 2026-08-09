export const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';
export const SERVER_API_URL = process.env.API_URL || CLIENT_API_URL;

export class ApiError extends Error {
  constructor(public status: number, public message: string, public data?: unknown) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Type-narrowing helper for parsed API error response bodies. */
function extractErrorMessage(data: unknown, fallback: string): string {
  if (data !== null && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    // Genesis error envelope: { error: { message: string } }
    if (obj['error'] !== null && typeof obj['error'] === 'object') {
      const err = obj['error'] as Record<string, unknown>;
      if (typeof err['message'] === 'string') return err['message'];
    }
    // FastAPI default: { detail: string }
    if (typeof obj['detail'] === 'string') return obj['detail'];
    // Client-side proxy error: { error: string }
    if (typeof obj['error'] === 'string') return obj['error'];
  }
  return fallback;
}

/**
 * Server-side API fetch wrapper that injects the auth token from cookies.
 * Should only be called from Server Components or API Routes.
 */
export async function fetchServerApi(endpoint: string, options: RequestInit = {}): Promise<unknown> {
  const { cookies } = await import('next/headers');
  const cookieStore = await cookies();
  const token = cookieStore.get('genesis_token')?.value;

  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const res = await fetch(`${SERVER_API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = 'API Error';
    let data: unknown;
    try {
      data = await res.json();
      message = extractErrorMessage(data, res.statusText);
    } catch {
      message = res.statusText;
    }
    throw new ApiError(res.status, message, data);
  }

  if (res.status === 204) return null;
  return res.json();
}

/**
 * Client-side API fetch wrapper.
 * For auth routes it talks to our Next.js API proxy to set/clear httpOnly cookies.
 * For other routes it calls the Next.js API proxy to attach the token.
 */
export async function fetchClientApi(endpoint: string, options: RequestInit = {}): Promise<unknown> {
  // Route auth endpoints directly to Next.js API routes (they set/clear httpOnly cookies).
  // All other requests go through the proxy route which attaches the Bearer token.
  const isAuthNextjsRoute = endpoint.startsWith('/api/auth');
  const url = isAuthNextjsRoute ? endpoint : `/api/proxy${endpoint}`;

  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = 'API Error';
    let data: unknown;
    try {
      data = await res.json();
      message = extractErrorMessage(data, res.statusText);
    } catch {
      message = res.statusText;
    }
    throw new ApiError(res.status, message, data);
  }

  if (res.status === 204) return null;
  return res.json();
}
