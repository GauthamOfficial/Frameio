import { NextRequest, NextResponse } from "next/server";

const isPublicRoute = (pathname: string): boolean => {
  const publicRoutes = [
    "/",
    "/sign-in",
    "/sign-up",
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

  // Handle admin routes with custom authentication
  if (pathname.startsWith('/admin') || pathname.startsWith('/api/admin')) {
    // Admin API routes - allow through
    if (pathname.startsWith('/api/admin')) {
      return NextResponse.next();
    }

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

  // Check for authentication token in cookies
  // Tokens are stored in both localStorage (for client-side) and cookies (for middleware)
  const authToken = req.cookies.get('auth_token')?.value || 
                    req.headers.get('authorization')?.replace('Bearer ', '');

  if (!authToken) {
    // Redirect to sign-in if not authenticated
    // Check referer to avoid redirect loops from sign-in/sign-up pages
    const referer = req.headers.get('referer') || ''
    const isFromAuthPage = referer.includes('/sign-in') || referer.includes('/sign-up')
    
    if (!isFromAuthPage) {
      const signInUrl = new URL('/sign-in', req.url);
      signInUrl.searchParams.set('redirect_url', pathname);
      return NextResponse.redirect(signInUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
