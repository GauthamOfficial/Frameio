import { NextResponse } from 'next/server';
import { getAdminSession } from '@/lib/admin-auth';

export async function GET() {
  try {
    const session = await getAdminSession();
    
    if (!session) {
      // Return 200 with authenticated: false instead of 401
      // This prevents console errors when checking auth status
      return NextResponse.json(
        { authenticated: false },
        { status: 200 }
      );
    }

    return NextResponse.json(
      { 
        authenticated: true,
        username: session.username,
        loginTime: session.loginTime,
        expiresAt: session.expiresAt
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Admin session verification error:', error);
    return NextResponse.json(
      { authenticated: false },
      { status: 200 }
    );
  }
}

