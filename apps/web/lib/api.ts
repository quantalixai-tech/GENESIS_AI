export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export class ApiError extends Error {
  constructor(public status: number, public message: string, public data?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Server-side API fetch wrapper that injects the auth token from cookies.
 * Should only be called from Server Components or API Routes.
 */
export async function fetchServerApi(endpoint: string, options: RequestInit = {}) {
  const { cookies } = await import('next/headers');
  const cookieStore = await cookies();
  const token = cookieStore.get('genesis_token')?.value;

  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = 'API Error';
    let data;
    try {
      data = await res.json();
      message = data.error?.message || data.detail || message;
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
export async function fetchClientApi(endpoint: string, options: RequestInit = {}) {
  // If the endpoint is an absolute path that starts with /api (Next.js route)
  // or we want to proxy everything via Next.js to handle tokens transparently.
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
    let data;
    try {
      data = await res.json();
      message = data.error || data.detail || message;
    } catch {
      message = res.statusText;
    }
    throw new ApiError(res.status, message, data);
  }

  if (res.status === 204) return null;
  return res.json();
}
