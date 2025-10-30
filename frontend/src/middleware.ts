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

  // Apply Clerk authentication for non-admin routes
  if (!isPublicRoute(req)) {
    const { userId } = await auth();
    if (!userId) {
      return new Response("Unauthorized", { status: 401 });
    }
  }
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
