import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { API_BASE_URL } from '../../../../lib/api';

async function handleRequest(request: Request, { params }: { params: Promise<{ route: string[] }> }) {
  const resolvedParams = await params;
  const route = resolvedParams.route.join('/');
  const searchParams = new URL(request.url).search;
  
  const cookieStore = await cookies();
  const token = cookieStore.get('genesis_token')?.value;

  const headers = new Headers(request.headers);
  headers.delete('host'); // Let fetch set the correct host
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const fetchOptions: RequestInit = {
      method: request.method,
      headers,
    };

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      const clonedRequest = request.clone();
      const contentType = request.headers.get('content-type') || '';
      
      if (contentType.includes('multipart/form-data')) {
        fetchOptions.body = await clonedRequest.formData();
      } else {
        fetchOptions.body = await clonedRequest.text();
      }
    }

    const res = await fetch(`${API_BASE_URL}/${route}${searchParams}`, fetchOptions);
    
    // Copy headers from response
    const responseHeaders = new Headers();
    res.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });

    if (res.status === 204) {
      return new NextResponse(null, { status: 204, headers: responseHeaders });
    }

    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error(`API proxy error (${route}):`, error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = handleRequest;
export const POST = handleRequest;
export const PUT = handleRequest;
export const PATCH = handleRequest;
export const DELETE = handleRequest;
