import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

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

export default clerkMiddleware((auth, req) => {
  // Only protect non-admin routes
  if (!isPublicRoute(req) && isProtectedRoute(req)) {
    auth().protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};

