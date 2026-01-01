import { NextRequest, NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';
import { buildApiUrl } from '@/utils/api';

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

    // Get query parameters
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    // Note: Don't add is_active filter - admin panel should show all templates
    const url = buildApiUrl(`/api/ai/poster-templates/${queryString ? `?${queryString}` : ''}`);

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
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown network error';
      console.error('Admin templates fetch network error:', errorMessage);
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: 'Unable to connect to the backend server. Please ensure the backend is running and accessible.',
          networkError: true
        },
        { status: 503 }
      );
    }

    let data: Record<string, unknown> | unknown[];
    try {
      const text = await response.text();
      if (text) {
        data = JSON.parse(text);
      } else {
        data = [];
      }
    } catch {
      data = [];
    }

    if (!response.ok) {
      const errorData = Array.isArray(data) ? {} : data as Record<string, unknown>;
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { 
            error: errorData.error || 'Authentication failed',
            detail: errorData.detail || errorData.message || 'Please ensure you are logged into the admin panel'
          },
          { status: response.status }
        );
      }
      return NextResponse.json(
        { 
          error: errorData.error || errorData.detail || errorData.message || `Failed to fetch templates (${response.status})`,
          detail: errorData.detail || errorData.message || `Backend returned status ${response.status}`
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Admin templates fetch error:', errorMessage, error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        detail: errorMessage || 'An unexpected error occurred while fetching templates'
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
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

    // Get form data from request
    const formData = await request.formData();

    // Forward request to Django backend with admin header
    const url = buildApiUrl('/api/ai/poster-templates/');
    
    let response: Response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: {
          'X-Admin-Request': 'true',
          'X-Admin-Username': session.username,
        },
        body: formData,
      });
    } catch (fetchError) {
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown network error';
      console.error('Admin templates create network error:', errorMessage);
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: 'Unable to connect to the backend server.',
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
      data = {};
    }

    if (!response.ok) {
      return NextResponse.json(
        { 
          error: data.error || data.detail || data.message || `Failed to create template (${response.status})`,
          detail: data.detail || data.message
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Admin templates create error:', errorMessage, error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        detail: errorMessage || 'An unexpected error occurred while creating template'
      },
      { status: 500 }
    );
  }
}

