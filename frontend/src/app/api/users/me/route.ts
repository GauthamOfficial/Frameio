import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Simple token getter - in development, use test token
function getAuthToken(request: NextRequest): string | null {
  // Check for token in Authorization header
  const authHeader = request.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.split(' ')[1];
  }
  
  // In development, use test token
  if (process.env.NODE_ENV === 'development') {
    return 'test_clerk_token';
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

    // Get current user from backend
    const response = await fetch(`${API_BASE_URL}/api/users/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || data.message || 'Failed to fetch user profile' },
        { status: response.status }
      );
    }

    // If the response is an array, get the first user (current user)
    const user = Array.isArray(data) ? data[0] : data;
    return NextResponse.json(user, { status: response.status });
  } catch (error) {
    console.error('User profile fetch error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const token = getAuthToken(request);

    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const body = await request.json();

    // First, get the current user to find their backend user ID
    const getUserResponse = await fetch(`${API_BASE_URL}/api/users/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!getUserResponse.ok) {
      const errorData = await getUserResponse.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || errorData.message || 'Failed to fetch user' },
        { status: getUserResponse.status }
      );
    }

    const users = await getUserResponse.json();
    
    // Find the current user by email (from the request body or from the users list)
    let currentUser: any;
    if (Array.isArray(users)) {
      if (body.email) {
        currentUser = users.find((u: any) => u.email === body.email);
      }
      if (!currentUser && users.length > 0) {
        currentUser = users[0];
      }
    } else {
      currentUser = users;
    }
    
    if (!currentUser || !currentUser.id) {
      return NextResponse.json(
        { error: 'User not found. Please ensure you are part of an organization.' },
        { status: 404 }
      );
    }

    // Remove email from body as it's not part of the update
    const { email, ...updateData } = body;

    // Update the user profile
    const updateResponse = await fetch(`${API_BASE_URL}/api/users/${currentUser.id}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });

    const responseData = await updateResponse.json().catch(() => ({}));

    if (!updateResponse.ok) {
      return NextResponse.json(
        { error: responseData.detail || responseData.message || responseData.error || 'Failed to update profile' },
        { status: updateResponse.status }
      );
    }

    return NextResponse.json(responseData, { status: updateResponse.status });
  } catch (error) {
    console.error('User profile update error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
