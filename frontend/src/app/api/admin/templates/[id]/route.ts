import { NextRequest, NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';
import { buildApiUrl } from '@/utils/api';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const url = buildApiUrl(`/api/ai/poster-templates/${params.id}/`);
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
    });

    const data = await response.json();
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
  { params }: { params: { id: string } }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const formData = await request.formData();
    const url = buildApiUrl(`/api/ai/poster-templates/${params.id}/`);
    
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
  { params }: { params: { id: string } }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const url = buildApiUrl(`/api/ai/poster-templates/${params.id}/`);
    
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Request': 'true',
        'X-Admin-Username': session.username,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
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
  { params }: { params: { id: string } }
) {
  try {
    const session = await getAdminSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const url = buildApiUrl(`/api/ai/poster-templates/${params.id}/`);
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

