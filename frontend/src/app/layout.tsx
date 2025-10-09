import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { SimpleErrorBoundary } from "@/components/simple-error-boundary";
import { ClerkErrorBoundary } from "@/components/auth/clerk-error-boundary";
import { AppProvider } from "@/contexts/app-context";
import { OrganizationProvider } from "@/contexts/organization-context";
import { ToastProvider } from "@/components/common";
import { AppLayoutWrapper } from "@/components/layout/app-layout-wrapper";
import "./globals.css";
import "@/lib/test-data"; // Import test data utilities
import "@/lib/wallet-error-handler"; // Handle wallet connection errors
import "@/lib/chunk-error-handler"; // Handle chunk loading errors

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Frameio - AI-Powered Textile Design Platform",
  description: "Transform your textile business with AI-powered design generation, smart fabric analysis, and automated catalog creation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkErrorBoundary>
      <ClerkProvider
        appearance={{
          baseTheme: dark,
          variables: {
            colorPrimary: '#3b82f6',
          },
        }}
        publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
        afterSignInUrl="/dashboard"
        afterSignUpUrl="/dashboard"
        signInUrl="/sign-in"
        signUpUrl="/sign-up"
        frontendApi={process.env.NEXT_PUBLIC_CLERK_FRONTEND_API}
      >
        <html lang="en">
          <head>
            <meta name="ethereum-dapp-url-bar" content="false" />
            <meta name="ethereum-dapp-metamask" content="false" />
            <meta httpEquiv="Content-Security-Policy" content={`script-src 'self' 'unsafe-inline' 'unsafe-eval' https://clerk.com https://*.clerk.com ${process.env.NEXT_PUBLIC_CLERK_FRONTEND_API}; object-src 'none';`} />
          </head>
          <body
            className={`${geistSans.variable} ${geistMono.variable} antialiased`}
          >
            <SimpleErrorBoundary>
              <ToastProvider>
                <AppProvider>
                  <OrganizationProvider>
                    <AppLayoutWrapper>
                      {children}
                    </AppLayoutWrapper>
                  </OrganizationProvider>
                </AppProvider>
              </ToastProvider>
            </SimpleErrorBoundary>
          </body>
        </html>
      </ClerkProvider>
    </ClerkErrorBoundary>
  );
}

