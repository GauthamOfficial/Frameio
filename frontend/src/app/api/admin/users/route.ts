import { NextRequest, NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
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
    const response = await fetch(`${API_BASE_URL}/api/users/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
    });

    const data = await response.json().catch(() => []);

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
        { error: data.detail || data.message || 'Failed to fetch users' },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Admin users fetch error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}






