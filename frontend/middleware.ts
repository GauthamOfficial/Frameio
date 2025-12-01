import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

// Clerk-protected routes (user routes only)
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/ai-poster-generator(.*)',
  '/settings(.*)',
]);

// Admin routes should be excluded from Clerk
const isPublicRoute = createRouteMatcher([
  '/admin(.*)',
  '/api/admin(.*)',
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
]);

export default clerkMiddleware(async (auth, req: NextRequest) => {
  // Only protect non-admin routes
  if (!isPublicRoute(req) && isProtectedRoute(req)) {
    const authResult = await auth();
    if (!authResult.userId) {
      // Redirect to sign-in if not authenticated
      const signInUrl = new URL('/sign-in', req.url);
      signInUrl.searchParams.set('redirect_url', req.nextUrl.pathname);
      return NextResponse.redirect(signInUrl);
    }
  }
  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};

