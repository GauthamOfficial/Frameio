import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  outputFileTracingRoot: 'D:\\My Files\\Yarl IT Hub\\Framio',
  images: {
    domains: ['localhost', '127.0.0.1'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'https',
        hostname: '*.ngrok.io',
        pathname: '/media/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8000/api/ai/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/health',
        destination: 'http://localhost:8000/health/',
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://clerk.com https://*.clerk.com https://sound-mule-24.clerk.accounts.dev",
              "worker-src 'self' blob:", // Allow blob workers for Clerk
              "child-src 'self' blob:",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob: https:",
              "font-src 'self' data:",
              "connect-src 'self' https://clerk.com https://*.clerk.com https://sound-mule-24.clerk.accounts.dev http://localhost:8000 ws://localhost:3000",
              "frame-src 'self' https://clerk.com https://*.clerk.com",
            ].join('; '),
          },
        ],
      },
    ]
  },
  // Improve chunk loading reliability
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        ...config.optimization.splitChunks,
        cacheGroups: {
          ...config.optimization.splitChunks?.cacheGroups,
          clerk: {
            test: /[\\/]node_modules[\\/]@clerk[\\/]/,
            name: 'clerk',
            chunks: 'all',
            priority: 20,
          },
        },
      }
    }
    return config
  },
  // Add experimental features for better chunk loading
  experimental: {
    optimizePackageImports: ['@clerk/nextjs', '@clerk/themes'],
  },
};

export default nextConfig;
