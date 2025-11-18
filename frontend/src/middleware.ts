import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhooks(.*)",
  "/poster(.*)",  // Allow public access to poster sharing pages
  "/admin(.*)",   // Admin routes handled separately
  "/api/admin(.*)" // Admin API routes
]);

export default clerkMiddleware(async (auth, req: NextRequest) => {
  const { pathname } = req.nextUrl;

  // Handle admin routes with custom authentication
  if (pathname.startsWith('/admin') || pathname.startsWith('/api/admin')) {
    // Admin API routes - allow through
    if (pathname.startsWith('/api/admin')) {
      return NextResponse.next();
    }

    // Admin login route - redirect if already authenticated
    if (pathname === '/admin/login') {
      const adminSession = req.cookies.get('admin-session');
      if (adminSession) {
        return NextResponse.redirect(new URL('/admin', req.url));
      }
      return NextResponse.next();
    }

    // Protected admin pages - redirect to login if not authenticated
    if (pathname.startsWith('/admin')) {
      const adminSession = req.cookies.get('admin-session');
      if (!adminSession) {
        return NextResponse.redirect(new URL('/admin/login', req.url));
      }
      return NextResponse.next();
    }
  }

  // Allow public routes to pass through
  if (isPublicRoute(req)) {
    return NextResponse.next();
  }

  // Protect all other routes with Clerk authentication
  const authResult = await auth();
  
  if (!authResult.userId) {
    // Redirect to sign-in if not authenticated
    const signInUrl = new URL('/sign-in', req.url);
    signInUrl.searchParams.set('redirect_url', pathname);
    return NextResponse.redirect(signInUrl);
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
