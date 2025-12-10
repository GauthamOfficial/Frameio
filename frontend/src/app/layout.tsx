import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { SimpleErrorBoundary } from "@/components/simple-error-boundary";
import { AppProvider } from "@/contexts/app-context";
import { OrganizationProvider } from "@/contexts/organization-context";
import { ToastProvider } from "@/components/common";
import { AppLayoutWrapper } from "@/components/layout/app-layout-wrapper";
import MetaMaskSuppressor from "@/components/MetaMaskSuppressor";
import "./globals.css";
import "@/lib/test-data"; // Import test data utilities
import "@/lib/wallet-error-handler"; // Handle wallet connection errors
import "@/lib/meta-mask-suppressor"; // Comprehensive MetaMask suppression
import "@/lib/chunk-error-handler"; // Handle chunk loading errors
import "@/lib/test-data"; // Import test data utilities

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
    <html lang="en">
      <head>
        <meta name="ethereum-dapp-url-bar" content="false" />
        <meta name="ethereum-dapp-metamask" content="false" />
        <meta name="ethereum-dapp-connect" content="false" />
        <meta name="ethereum-dapp-wallet" content="false" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Prevent MetaMask from auto-connecting
              if (typeof window !== 'undefined') {
                window.ethereum = undefined;
                window.web3 = undefined;
                
                // Override any wallet detection
                Object.defineProperty(window, 'ethereum', {
                  value: undefined,
                  writable: false,
                  configurable: false
                });
              }
            `,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <SimpleErrorBoundary>
          <MetaMaskSuppressor />
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
  );
}

