import { NextRequest, NextResponse } from 'next/server';
import { validateRedirectPath, validateJWTToken } from '@/lib/security/input-validation';
import { checkRateLimit, RateLimitPresets } from '@/lib/security/rate-limit';

async function handleRequest(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const accessToken = searchParams.get('access');
  const refreshToken = searchParams.get('refresh');
  
  // Get base URL from environment variable or extract from request
  // CRITICAL: In production, always use NEXT_PUBLIC_APP_URL, never fallback to request.url.origin
  // because request.url.origin might be the backend IP (47.129.60.11) instead of the frontend domain
  let baseUrl = process.env.NEXT_PUBLIC_APP_URL;
  
  // Runtime production detection: check if request is from production domain
  const requestOrigin = new URL(request.url).origin;
  const isProductionDomain = requestOrigin.includes('frameio.co') || 
    request.headers.get('host')?.includes('frameio.co');
  
  if (!baseUrl) {
    if (isProductionDomain) {
      // We're on production domain - use it
      baseUrl = 'https://frameio.co';
      if (process.env.NODE_ENV === 'development') {
        console.warn('NEXT_PUBLIC_APP_URL not set. Using https://frameio.co as fallback.');
      }
    } else {
      // Development fallback
      baseUrl = requestOrigin;
    }
  }
  
  // Final safety check: never use localhost or backend IP when on production domain
  if (isProductionDomain) {
    if (baseUrl.includes('localhost') || baseUrl.includes('47.129.60.11')) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Warning: Invalid URL detected. Using https://frameio.co');
      }
      baseUrl = 'https://frameio.co';
    }
  }

  // Validate tokens
  if (!accessToken || !refreshToken) {
    return NextResponse.redirect(new URL('/sign-in?error=invalid_tokens', baseUrl));
  }
  
  // Validate token format using security utility
  if (!validateJWTToken(accessToken) || !validateJWTToken(refreshToken)) {
    return NextResponse.redirect(new URL('/sign-in?error=invalid_token_format', baseUrl));
  }

  // Get and validate redirect path
  const rawRedirect = searchParams.get('redirect') || '/dashboard';
  const redirectTo = validateRedirectPath(rawRedirect);
  
  // Create redirect URL - ensure it stays on same origin
  let redirectUrl: URL;
  try {
    redirectUrl = new URL(redirectTo, baseUrl);
    
    // CRITICAL: Ensure redirect stays on same origin to prevent open redirect
    const baseUrlObj = new URL(baseUrl);
    if (redirectUrl.origin !== baseUrlObj.origin) {
      // If redirect would go to different origin, force to dashboard
      redirectUrl = new URL('/dashboard', baseUrl);
    }
  } catch {
    // If URL construction fails, default to dashboard
    redirectUrl = new URL('/dashboard', baseUrl);
  }
  
  // Only add verified parameter if redirecting to dashboard
  if (redirectTo === '/dashboard') {
    redirectUrl.searchParams.set('verified', 'true');
  }
  
  const response = NextResponse.redirect(redirectUrl);

  // Set cookies with secure configuration
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds
  const isProduction = process.env.NODE_ENV === 'production';

  // SECURITY: Use httpOnly for auth tokens to prevent XSS attacks
  // If you need client-side access, consider using a separate non-sensitive cookie
  // or implement a secure API endpoint to retrieve token info
  response.cookies.set('auth_token', accessToken, {
    httpOnly: true, // ✅ SECURE: Prevents JavaScript access (XSS protection)
    secure: isProduction, // Only send over HTTPS in production
    sameSite: 'lax', // CSRF protection
    maxAge: maxAge,
    path: '/',
  });

  response.cookies.set('refresh_token', refreshToken, {
    httpOnly: true, // ✅ SECURE: Prevents JavaScript access (XSS protection)
    secure: isProduction, // Only send over HTTPS in production
    sameSite: 'lax', // CSRF protection
    maxAge: maxAge,
    path: '/',
  });

  return response;
}

export async function GET(request: NextRequest) {
  // Apply rate limiting for auth endpoints
  const rateLimitResult = checkRateLimit(
    new Request(request.url, { headers: request.headers }),
    RateLimitPresets.auth
  );

  if (!rateLimitResult.allowed) {
    return NextResponse.json(
      {
        error: RateLimitPresets.auth.message,
        retryAfter: rateLimitResult.retryAfter,
      },
      {
        status: 429,
        headers: {
          'Retry-After': String(rateLimitResult.retryAfter || 60),
          'X-RateLimit-Limit': String(RateLimitPresets.auth.maxRequests),
          'X-RateLimit-Remaining': String(rateLimitResult.remaining),
          'X-RateLimit-Reset': String(rateLimitResult.resetTime),
        },
      }
    );
  }

  return handleRequest(request);
}

