import { NextRequest, NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';

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
    
    // In development, use absolute URL to bypass Next.js rewrites
    const backendUrl = getDjangoBackendUrl();
    // Construct endpoint properly - Django REST Framework expects trailing slash
    const endpoint = queryString 
      ? `/api/ai/poster-templates/?${queryString}`
      : `/api/ai/poster-templates/`;
    // Always use absolute URL in API routes (server-side) to ensure proper connection
    const url = `${backendUrl}${endpoint}`;
    
    console.log('[Admin Templates API] Fetching from:', url);
    console.log('[Admin Templates API] Admin username:', session.username);

    // Forward request to Django backend with admin header
    let response: Response;
    try {
      console.log('[Admin Templates API] Making fetch request to:', url);
      console.log('[Admin Templates API] Headers:', {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      });
      
      response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Request': 'true',
          'X-Admin-Username': session.username,
        },
      });
      
      console.log('[Admin Templates API] Fetch completed, status:', response.status);
      console.log('[Admin Templates API] Response headers:', Object.fromEntries(response.headers.entries()));
    } catch (fetchError) {
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown network error';
      console.error('[Admin Templates API] Fetch network error:', errorMessage);
      console.error('[Admin Templates API] Error type:', fetchError instanceof Error ? fetchError.constructor.name : typeof fetchError);
      console.error('[Admin Templates API] Error stack:', fetchError instanceof Error ? fetchError.stack : 'No stack');
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: `Unable to connect to the backend server at ${url}. Error: ${errorMessage}. Please ensure the backend is running on ${backendUrl}.`,
          networkError: true,
          url: url,
          backendUrl: backendUrl
        },
        { status: 503 }
      );
    }

    const text = await response.text();
    
    // Check if response is HTML (Next.js fallback page)
    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
      console.error('[Admin Templates API] Backend returned HTML instead of JSON');
      console.error('[Admin Templates API] Response preview:', text.substring(0, 500));
      console.error('[Admin Templates API] Full URL was:', url);
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          detail: `Backend returned HTML error page instead of JSON. The endpoint ${url} may be incorrect or the server may be down. Please check that Django backend is running on ${backendUrl}.`,
          networkError: true,
          url: url,
          backendUrl: backendUrl,
          responsePreview: text.substring(0, 200)
        },
        { status: 503 }
      );
    }
    
    let data: Record<string, unknown> | unknown[];
    try {
      if (text) {
        data = JSON.parse(text);
        console.log('[Admin Templates API] Response status:', response.status);
        console.log('[Admin Templates API] Response type:', typeof data);
        console.log('[Admin Templates API] Is array:', Array.isArray(data));
        if (Array.isArray(data)) {
          console.log('[Admin Templates API] Templates count:', data.length);
        } else if (data && typeof data === 'object') {
          console.log('[Admin Templates API] Response keys:', Object.keys(data));
          if ('results' in data && Array.isArray(data.results)) {
            console.log('[Admin Templates API] Results count:', data.results.length);
          }
        }
      } else {
        console.warn('[Admin Templates API] Empty response text');
        data = [];
      }
    } catch (parseError) {
      // JSON parsing failed
      console.error('Failed to parse admin templates response:', parseError);
      console.error('Response text preview:', text.substring(0, 200));
      data = [];
    }

    if (!response.ok) {
      const errorData = Array.isArray(data) ? {} : data as Record<string, unknown>;
      console.error('[Admin Templates API] Error response:', {
        status: response.status,
        statusText: response.statusText,
        errorData
      });
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

    // Ensure we return an array even if backend returns empty array or different structure
    let templatesArray: unknown[] = [];
    if (Array.isArray(data)) {
      templatesArray = data;
      console.log('[Admin Templates API] Data is direct array, length:', templatesArray.length);
    } else if (data && typeof data === 'object') {
      if ('results' in data && Array.isArray(data.results)) {
        templatesArray = data.results;
        console.log('[Admin Templates API] Data has results array, length:', templatesArray.length);
      } else if ('data' in data && Array.isArray(data.data)) {
        templatesArray = data.data;
        console.log('[Admin Templates API] Data has data array, length:', templatesArray.length);
      } else {
        console.warn('[Admin Templates API] Unexpected data structure:', Object.keys(data));
        console.warn('[Admin Templates API] Full data:', JSON.stringify(data).substring(0, 500));
      }
    } else {
      console.warn('[Admin Templates API] Data is not array or object:', typeof data, data);
    }
    
    console.log('[Admin Templates API] Final templates array length:', templatesArray.length);
    if (templatesArray.length > 0) {
      console.log('[Admin Templates API] First template:', JSON.stringify(templatesArray[0]).substring(0, 200));
    } else {
      console.warn('[Admin Templates API] ⚠️ WARNING: Templates array is empty!');
      console.warn('[Admin Templates API] Response status was:', response.status);
      console.warn('[Admin Templates API] Original data type:', typeof data);
      console.warn('[Admin Templates API] Original data:', data);
    }
    
    return NextResponse.json(templatesArray, { status: response.status });
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
    // Always use absolute URL in API routes (server-side) to ensure proper connection
    const backendUrl = getDjangoBackendUrl();
    const url = `${backendUrl}/api/ai/poster-templates/`;
    
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

