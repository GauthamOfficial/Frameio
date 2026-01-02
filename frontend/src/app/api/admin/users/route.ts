import { NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';
import { buildApiUrl } from '@/utils/api';

// Get Django backend URL - same logic as other API routes
function getDjangoBackendUrl(): string {
  // Priority: NEXT_PUBLIC_API_URL > NEXT_PUBLIC_API_BASE_URL > development localhost
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '');
  }
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/+$/, '');
  }
  // Development fallback
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  // Production fallback
  return 'http://13.213.53.199';
}

export async function GET() {
  try {
    // Verify admin session
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { 
          error: 'Unauthorized - Please log in to the admin panel first',
          detail: 'Admin session required. Please visit /admin and log in.'
        },
        { status: 401 }
      );
    }

    // Get Django backend URL
    const backendUrl = getDjangoBackendUrl();
    // In development, use absolute URL to bypass Next.js rewrites
    // In production, use buildApiUrl for relative paths
    const url = process.env.NODE_ENV === 'development' 
      ? `${backendUrl}/api/users/`
      : buildApiUrl('/api/users/');

    // Forward request to Django backend with admin header
    let response: Response;
    try {
      response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Request': 'true',
          'X-Admin-Username': session.username,
        },
      });
    } catch (fetchError) {
      // Handle network errors (backend not accessible, CORS, etc.)
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown network error';
      console.error('Admin users fetch network error:', errorMessage);
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: 'Unable to connect to the backend server. Please ensure the backend is running and accessible.',
          networkError: true
        },
        { status: 503 }
      );
    }

    const text = await response.text();

    // Check if response is HTML (Next.js fallback page)
    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
      console.error('Backend returned HTML instead of JSON for admin users');
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: 'Backend returned HTML error page. The endpoint may be incorrect or the server may be down.',
          networkError: true
        },
        { status: 503 }
      );
    }

    let data: Record<string, unknown>;
    try {
      if (text) {
        data = JSON.parse(text);
      } else {
        data = {};
      }
    } catch (parseError) {
      // JSON parsing failed
      console.error('Failed to parse admin users response:', parseError);
      return NextResponse.json(
        { 
          error: 'Invalid response from backend',
          detail: 'Backend returned non-JSON response. Please check backend logs.',
          networkError: true
        },
        { status: 503 }
      );
    }

    if (!response.ok) {
      // If it's an authentication error, provide helpful message
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { 
            error: data.error || 'Authentication failed',
            detail: data.detail || data.message || 'Please ensure you are logged into the admin panel and ADMIN_USERNAME is configured correctly in the backend .env file'
          },
          { status: response.status }
        );
      }
      return NextResponse.json(
        { 
          error: data.error || data.detail || data.message || `Failed to fetch users (${response.status})`,
          detail: data.detail || data.message || `Backend returned status ${response.status}`
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    // Handle unexpected errors
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Admin users fetch error:', errorMessage, error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        detail: errorMessage || 'An unexpected error occurred while fetching users'
      },
      { status: 500 }
    );
  }
}






