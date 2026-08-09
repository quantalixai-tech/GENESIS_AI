import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { SERVER_API_URL } from '../../../../lib/api';

export async function POST(request: Request, { params }: { params: Promise<{ route: string[] }> }) {
  const resolvedParams = await params;
  const route = resolvedParams.route.join('/');
  
  if (route === 'logout') {
    const cookieStore = await cookies();
    cookieStore.delete('genesis_token');
    return NextResponse.json({ success: true });
  }

  if (route === 'login' || route === 'signup') {
    try {
      const body = await request.json();
      
      let fetchOptions: RequestInit = {
        method: 'POST',
      };

      if (route === 'login') {
        const formData = new URLSearchParams();
        formData.append('username', body.email);
        formData.append('password', body.password);
        fetchOptions.headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
        fetchOptions.body = formData.toString();
      } else {
        fetchOptions.headers = { 'Content-Type': 'application/json' };
        fetchOptions.body = JSON.stringify(body);
      }

      const res = await fetch(`${SERVER_API_URL}/auth/${route}`, fetchOptions);
      const data = await res.json();

      if (!res.ok) {
        return NextResponse.json(
          { error: data.error?.message || data.detail || 'Authentication failed' },
          { status: res.status }
        );
      }

      const response = NextResponse.json({ user: data.user });
      
      // Set the HTTP-only cookie
      response.cookies.set({
        name: 'genesis_token',
        value: data.access_token,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 60 * 60 * 24 * 7, // 1 week
      });

      return response;
    } catch (error) {
      console.error(`Auth proxy error (${route}):`, error);
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
  }

  return NextResponse.json({ error: 'Not found' }, { status: 404 });
}
