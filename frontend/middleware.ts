import { NextRequest, NextResponse } from "next/server";

const isPublicRoute = (pathname: string): boolean => {
  const publicRoutes = [
    "/",
    "/sign-in",
    "/sign-up",
    "/forgot-password",
    "/reset-password",
    "/verify-email",
    "/check-email",
    "/api/webhooks",
    "/poster",
    "/admin/login",
  ];
  
  return publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + "/")
  );
};

export default function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // CRITICAL: Allow all API routes to pass through without authentication checks
  // API routes handle their own authentication or proxy to Django backend
  if (pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // Handle admin routes with custom authentication
  if (pathname.startsWith('/admin')) {
    // Admin login route - redirect if already authenticated
    if (pathname === '/admin/login') {
      const authToken = req.cookies.get('auth_token');
      if (authToken) {
        return NextResponse.redirect(new URL('/admin', req.url));
      }
      return NextResponse.next();
    }

    // Protected admin pages - redirect to login if not authenticated
    if (pathname.startsWith('/admin')) {
      const authToken = req.cookies.get('auth_token');
      if (!authToken) {
        return NextResponse.redirect(new URL('/admin/login', req.url));
      }
      return NextResponse.next();
    }
  }

  // Allow public routes to pass through
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }

  // Check for authentication token for frontend pages only
  const authToken = req.cookies.get('auth_token')?.value || 
                    req.headers.get('authorization')?.replace('Bearer ', '');

  if (!authToken) {
    // Check localStorage is not available in middleware, so redirect to sign-in
    const signInUrl = new URL('/sign-in', req.url);
    signInUrl.searchParams.set('redirect_url', pathname);
    return NextResponse.redirect(signInUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
