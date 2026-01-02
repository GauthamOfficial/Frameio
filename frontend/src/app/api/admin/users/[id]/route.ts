import { NextRequest, NextResponse } from 'next/server';
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

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    console.log('[Admin API PATCH] Starting patch request');
    
    // Verify admin session
    const session = await getAdminSession();
    console.log('[Admin API PATCH] Session check:', !!session);
    
    if (!session) {
      console.error('[Admin API PATCH] No session found');
      return NextResponse.json(
        { error: 'Unauthorized - Admin session required' },
        { status: 401 }
      );
    }

    const body = await request.json();
    console.log('[Admin API PATCH] Request body:', body);
    
    console.log('[Admin API PATCH] Awaiting params...');
    const { id: userId } = await params;
    console.log(`[Admin API PATCH] User ID: ${userId}`);
    
    // Get Django backend URL
    const backendUrl = getDjangoBackendUrl();
    // In development, use absolute URL to bypass Next.js rewrites
    // In production, use buildApiUrl for relative paths
    const djangoUrl = process.env.NODE_ENV === 'development'
      ? `${backendUrl}/api/users/${userId}/`
      : buildApiUrl(`/api/users/${userId}/`);
    console.log(`[Admin API PATCH] Django URL: ${djangoUrl}`);

    // Forward request to Django backend with admin header
    // Note: Django backend needs to be configured to accept X-Admin-Request header
    const response = await fetch(djangoUrl, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
      body: JSON.stringify(body),
    });

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const text = await response.text();

    // Check if response is HTML (Next.js fallback page)
    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
      console.error('Backend returned HTML instead of JSON for admin user PATCH');
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: 'Backend returned HTML error page. The endpoint may be incorrect or the server may be down.',
          networkError: true
        },
        { status: 503 }
      );
    }

    let data: Record<string, unknown> = {};
    if (isJson && text) {
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('Failed to parse admin user PATCH response:', parseError);
      }
    }

    if (!response.ok) {
      // If it's an authentication error, provide helpful message
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { 
            error: 'Django backend authentication required. Please configure admin authentication in Django backend.',
            detail: data.detail || data.message || 'Authentication failed'
          },
          { status: response.status }
        );
      }
      return NextResponse.json(
        { error: data.detail || data.message || 'Failed to update user' },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[Admin API PATCH] Error:', error);
    console.error('[Admin API PATCH] Error stack:', error instanceof Error ? error.stack : 'No stack');
    console.error('[Admin API PATCH] Error message:', error instanceof Error ? error.message : String(error));
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        detail: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    console.log('[Admin API DELETE] Starting delete request');
    
    // Verify admin session
    const session = await getAdminSession();
    console.log('[Admin API DELETE] Session check:', !!session);
    
    if (!session) {
      console.error('[Admin API DELETE] No session found');
      return NextResponse.json(
        { error: 'Unauthorized - Admin session required' },
        { status: 401 }
      );
    }

    console.log('[Admin API DELETE] Awaiting params...');
    const { id: userId } = await params;
    console.log(`[Admin API DELETE] User ID: ${userId}`);
    
    // Get Django backend URL
    const backendUrl = getDjangoBackendUrl();
    // In development, use absolute URL to bypass Next.js rewrites
    // In production, use buildApiUrl for relative paths
    const djangoUrl = process.env.NODE_ENV === 'development'
      ? `${backendUrl}/api/users/${userId}/`
      : buildApiUrl(`/api/users/${userId}/`);
    console.log(`[Admin API DELETE] Django URL: ${djangoUrl}`);

    // Forward request to Django backend with admin header
    // Note: Django backend needs to be configured to accept X-Admin-Request header
    const response = await fetch(djangoUrl, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
    });

    console.log(`[Admin API] Delete response status: ${response.status}`);

    if (!response.ok) {
      const contentType = response.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');
      const text = await response.text();

      // Check if response is HTML (Next.js fallback page)
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        console.error('Backend returned HTML instead of JSON for admin user DELETE');
        return NextResponse.json(
          { 
            error: 'Backend service unavailable',
            detail: 'Backend returned HTML error page. The endpoint may be incorrect or the server may be down.',
            networkError: true
          },
          { status: 503 }
        );
      }

      let data: Record<string, unknown> = {};
      if (isJson && text) {
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          console.error('Failed to parse admin user DELETE response:', parseError);
        }
      }
      console.error(`[Admin API] Delete failed:`, data);
      
      // If it's an authentication error, provide helpful message
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { 
            error: 'Django backend authentication required. Please configure admin authentication in Django backend.',
            detail: data.detail || data.message || 'Authentication failed'
          },
          { status: response.status }
        );
      }
      
      // For 404, provide more specific error
      if (response.status === 404) {
        return NextResponse.json(
          { 
            error: `User with ID ${userId} not found in database`,
            detail: data.detail || data.message || 'User not found'
          },
          { status: response.status }
        );
      }
      
      return NextResponse.json(
        { error: data.detail || data.message || 'Failed to delete user' },
        { status: response.status }
      );
    }

    console.log(`[Admin API DELETE] User ${userId} deleted successfully`);
    return NextResponse.json(
      { success: true, message: 'User deleted successfully' },
      { status: 200 }
    );
  } catch (error) {
    console.error('[Admin API DELETE] Error:', error);
    console.error('[Admin API DELETE] Error stack:', error instanceof Error ? error.stack : 'No stack');
    console.error('[Admin API DELETE] Error message:', error instanceof Error ? error.message : String(error));
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        detail: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

