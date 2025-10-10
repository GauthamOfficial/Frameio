import { NextRequest, NextResponse } from "next/server";

// Temporary middleware without Clerk to get the app running
export default function middleware(req: NextRequest) {
  // Allow all requests for now - we'll add authentication back later
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
