import { NextRequest, NextResponse } from 'next/server';

// Get Django backend URL - same logic as next.config.ts
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
  return 'http://47.129.60.11';
}

// Simple token getter
function getAuthToken(request: NextRequest): string | null {
  // Check for token in Authorization header
  const authHeader = request.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.split(' ')[1];
  }
  
  return null;
}

export async function GET(request: NextRequest) {
  try {
    const token = getAuthToken(request);

    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get Django backend URL and construct the full endpoint
    const backendUrl = getDjangoBackendUrl();
    const backendEndpoint = `${backendUrl}/api/users/auth/me/`;

    // Get current user from Django backend directly
    const response = await fetch(backendEndpoint, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    // Check content type before parsing
    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');

    let data: unknown = {};
    
    if (isJson) {
      try {
        data = await response.json();
      } catch (jsonError) {
        // If JSON parsing fails, try to get text for error message
        const text = await response.text().catch(() => 'Failed to parse response');
        console.error('Failed to parse JSON response:', jsonError, 'Response:', text.substring(0, 200));
        return NextResponse.json(
          { error: 'Invalid JSON response from backend', details: text.substring(0, 200) },
          { status: 500 }
        );
      }
    } else {
      // Not JSON - likely HTML error page
      const text = await response.text().catch(() => 'Failed to read response');
      console.error('Backend returned non-JSON response:', {
        status: response.status,
        contentType,
        preview: text.substring(0, 200)
      });
      
      // If it's an HTML error page, provide a helpful error
      if (text.includes('<!DOCTYPE') || text.includes('<html')) {
        return NextResponse.json(
          { 
            error: 'Backend returned HTML instead of JSON. The Django server may not be running or the endpoint is incorrect.',
            status: response.status,
            endpoint: backendEndpoint
          },
          { status: response.status || 500 }
        );
      }
      
      // Try to extract error message from text
      return NextResponse.json(
        { 
          error: 'Unexpected response format from backend',
          details: text.substring(0, 200),
          status: response.status
        },
        { status: response.status || 500 }
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        { 
          error: (data as { detail?: string; message?: string; error?: string }).detail || 
                 (data as { detail?: string; message?: string; error?: string }).message || 
                 (data as { detail?: string; message?: string; error?: string }).error || 
                 'Failed to fetch user profile',
          status: response.status
        },
        { status: response.status }
      );
    }

    // Return the user data (Django returns { user: {...} })
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('User profile fetch error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

