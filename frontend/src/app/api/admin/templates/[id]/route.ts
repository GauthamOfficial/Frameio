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

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { id } = await params;
    // Always use absolute URL in API routes (server-side) to ensure proper connection
    const backendUrl = getDjangoBackendUrl();
    const url = `${backendUrl}/api/ai/poster-templates/${id}/`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
    });

    // Check content type before parsing
    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    
    let data: unknown;
    if (isJson) {
      try {
        data = await response.json();
      } catch (jsonError) {
        const text = await response.text().catch(() => '');
        if (text.includes('<!DOCTYPE') || text.includes('<html')) {
          return NextResponse.json(
            { error: 'Backend returned HTML error page instead of JSON' },
            { status: 500 }
          );
        }
        throw jsonError;
      }
    } else {
      const text = await response.text().catch(() => '');
      if (text.includes('<!DOCTYPE') || text.includes('<html')) {
        return NextResponse.json(
          { error: 'Backend returned HTML error page instead of JSON' },
          { status: 500 }
        );
      }
      try {
        data = JSON.parse(text);
      } catch {
        return NextResponse.json(
          { error: 'Invalid response format from backend' },
          { status: 500 }
        );
      }
    }
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Admin template fetch error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { id } = await params;
    const formData = await request.formData();
    // In development, use absolute URL to bypass Next.js rewrites
    const backendUrl = getDjangoBackendUrl();
    const url = process.env.NODE_ENV === 'development'
      ? `${backendUrl}/api/ai/poster-templates/${id}/`
      : buildApiUrl(`/api/ai/poster-templates/${id}/`);
    
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
      body: formData,
    });

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
          error: data.error || data.detail || data.message || `Failed to update template (${response.status})`,
          detail: data.detail || data.message
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Admin template update error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { id } = await params;
    const body = await request.json();
    // In development, use absolute URL to bypass Next.js rewrites
    const backendUrl = getDjangoBackendUrl();
    const url = process.env.NODE_ENV === 'development'
      ? `${backendUrl}/api/ai/poster-templates/${id}/`
      : buildApiUrl(`/api/ai/poster-templates/${id}/`);
    
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
      body: JSON.stringify(body),
    });

    // Check content type before parsing
    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    
    let data: unknown;
    if (isJson) {
      try {
        data = await response.json();
      } catch (jsonError) {
        const text = await response.text().catch(() => '');
        if (text.includes('<!DOCTYPE') || text.includes('<html')) {
          return NextResponse.json(
            { error: 'Backend returned HTML error page instead of JSON' },
            { status: 500 }
          );
        }
        throw jsonError;
      }
    } else {
      const text = await response.text().catch(() => '');
      if (text.includes('<!DOCTYPE') || text.includes('<html')) {
        return NextResponse.json(
          { error: 'Backend returned HTML error page instead of JSON' },
          { status: 500 }
        );
      }
      try {
        data = JSON.parse(text);
      } catch {
        return NextResponse.json(
          { error: 'Invalid response format from backend' },
          { status: 500 }
        );
      }
    }
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Admin template patch error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { id } = await params;
    // Always use absolute URL in API routes (server-side) to ensure proper connection
    const backendUrl = getDjangoBackendUrl();
    const url = `${backendUrl}/api/ai/poster-templates/${id}/`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
    });

    if (!response.ok) {
      let data: Record<string, unknown> = {};
      try {
        const text = await response.text();
        if (text) {
          data = JSON.parse(text);
        }
      } catch {}
      
      return NextResponse.json(
        { 
          error: data.error || data.detail || data.message || `Failed to delete template (${response.status})`
        },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    console.error('Admin template delete error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

