import { NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';
import { API_BASE_URL, buildApiUrl } from '@/utils/api';

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

    // Forward request to Django backend with admin header
    let response: Response;
    try {
      response = await fetch(buildApiUrl('/api/users/'), {
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

    let data: Record<string, unknown>;
    try {
      const text = await response.text();
      if (text) {
        data = JSON.parse(text);
      } else {
        data = {};
      }
    } catch {
      // If response is not JSON, use empty object
      data = {};
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






