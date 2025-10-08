import { authMiddleware } from "@clerk/nextjs";

// This example protects all routes including api/trpc routes
// Please edit this to allow other routes to be public as needed.
// See https://clerk.com/docs/references/nextjs/auth-middleware for more information about configuring your Middleware
export default authMiddleware({
  // Routes that can be accessed while signed out
  publicRoutes: ["/", "/sign-in", "/sign-up"],
  // Routes that can always be accessed, and have
  // no authentication information
  ignoredRoutes: ["/api/webhooks"],
  // Allow dashboard access for authenticated users
  afterAuth(auth, req) {
    // Allow access to dashboard if user is signed in
    if (auth.userId && req.nextUrl.pathname.startsWith('/dashboard')) {
      return;
    }
  },
});

export const config = {
  // Protects all routes, including api/trpc routes
  // Please edit this to allow other routes to be public as needed.
  // See https://clerk.com/docs/references/nextjs/auth-middleware for more information about configuring your Middleware
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};

