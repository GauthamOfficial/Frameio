import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const accessToken = searchParams.get('access');
  const refreshToken = searchParams.get('refresh');
  // Default redirect to dashboard after email verification
  const redirectTo = searchParams.get('redirect') || '/dashboard';

  // Get base URL from environment variable or extract from request
  // CRITICAL: In production, always use NEXT_PUBLIC_APP_URL, never fallback to request.url.origin
  // because request.url.origin might be the backend IP (13.213.53.199) instead of the frontend domain
  let baseUrl = process.env.NEXT_PUBLIC_APP_URL;
  
  // Runtime production detection: check if request is from production domain
  const requestOrigin = new URL(request.url).origin;
  const isProductionDomain = requestOrigin.includes('frameio.co') || 
    request.headers.get('host')?.includes('frameio.co');
  
  if (!baseUrl) {
    if (isProductionDomain) {
      // We're on production domain - use it
      baseUrl = 'https://frameio.co';
      console.warn('NEXT_PUBLIC_APP_URL not set. Using https://frameio.co as fallback.');
    } else {
      // Development fallback
      baseUrl = requestOrigin;
    }
  }
  
  // Final safety check: never use localhost or backend IP when on production domain
  if (isProductionDomain) {
    if (baseUrl.includes('localhost') || baseUrl.includes('13.213.53.199')) {
      console.error('Warning: Invalid URL detected. Using https://frameio.co');
      baseUrl = 'https://frameio.co';
    }
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

