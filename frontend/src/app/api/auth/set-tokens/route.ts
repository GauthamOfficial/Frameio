import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const accessToken = searchParams.get('access');
  const refreshToken = searchParams.get('refresh');
  // Default redirect to dashboard after email verification
  const redirectTo = searchParams.get('redirect') || '/dashboard';

  // Get base URL from environment variable or extract from request
  // Use NEXT_PUBLIC_APP_URL for production (e.g., https://frameio.co)
  // In Next.js API routes, request.url is always defined, so we can safely use it as fallback
  let baseUrl = process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin;
  
  // Safety check: never use localhost in production
  if (process.env.NODE_ENV === 'production' && baseUrl.includes('localhost')) {
    console.error('Warning: localhost detected in production redirect. Using request origin instead.');
    baseUrl = new URL(request.url).origin;
  }

  if (!accessToken || !refreshToken) {
    return NextResponse.redirect(new URL('/sign-in?error=invalid_tokens', baseUrl));
  }

  // Create response with redirect
  // Use baseUrl to ensure redirect goes to production domain (https://frameio.co), not localhost
  // For sign-in page, we don't need the verified parameter
  const redirectUrl = new URL(redirectTo, baseUrl);
  // Only add verified parameter if redirecting to dashboard
  if (redirectTo === '/dashboard') {
    redirectUrl.searchParams.set('verified', 'true');
  }
  const response = NextResponse.redirect(redirectUrl);

  // Set cookies with proper configuration
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds
  const isProduction = process.env.NODE_ENV === 'production';

  response.cookies.set('auth_token', accessToken, {
    httpOnly: false, // Allow client-side access for localStorage sync
    secure: isProduction,
    sameSite: 'lax',
    maxAge: maxAge,
    path: '/',
  });

  response.cookies.set('refresh_token', refreshToken, {
    httpOnly: false, // Allow client-side access for localStorage sync
    secure: isProduction,
    sameSite: 'lax',
    maxAge: maxAge,
    path: '/',
  });

  return response;
}

