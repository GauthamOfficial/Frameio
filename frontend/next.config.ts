import type { NextConfig } from "next";
import path from "path";

// Get API base URL from environment, with fallback for development
const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'development') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }
  // Production: use NEXT_PUBLIC_API_URL or fallback to EC2
  return process.env.NEXT_PUBLIC_API_URL || 'http://13.213.53.199/api';
};

const API_BASE_URL = getApiBaseUrl();
// Extract hostname and protocol from API_BASE_URL for CSP
const apiUrlObj = new URL(API_BASE_URL);
const apiHost = apiUrlObj.hostname;
const apiProtocol = apiUrlObj.protocol.slice(0, -1); // Remove trailing ':'

const nextConfig: NextConfig = {
  /* config options here */
  // Set outputFileTracingRoot to the frontend directory to avoid multiple lockfile warning
  outputFileTracingRoot: path.join(__dirname),
  images: {
    remotePatterns: [
      // Development patterns
      {
        protocol: 'http' as const,
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'http' as const,
        hostname: 'localhost',
        pathname: '/**',
      },
      {
        protocol: 'http' as const,
        hostname: '127.0.0.1',
        pathname: '/**',
      },
      // Production pattern (if API_BASE_URL is set)
      ...(apiHost !== 'localhost' && apiHost !== '127.0.0.1' ? [{
        protocol: apiProtocol as 'http' | 'https',
        hostname: apiHost,
        ...(apiUrlObj.port ? { port: apiUrlObj.port } : {}),
        pathname: '/**',
      }] : []),
      // ngrok pattern for tunneling
      {
        protocol: 'https' as const,
        hostname: '*.ngrok.io',
        pathname: '/media/**',
      },
    ],
  },
  async rewrites() {
    // In production, rewrites may not be needed if frontend and backend are on different domains
    // Only use rewrites in development or if API_BASE_URL is on same origin
    if (process.env.NODE_ENV === 'development' || apiHost === 'localhost' || apiHost === '127.0.0.1') {
      return [
        {
          source: '/api/ai/:path*',
          destination: `${API_BASE_URL}/api/ai/:path*`,
        },
        // Note: /api/admin/* routes are handled by Next.js API routes, not Django
        // Only forward non-admin API routes to Django
        {
          source: '/api/((?!admin).*)',
          destination: `${API_BASE_URL}/api/$1`,
        },
        {
          source: '/health',
          destination: `${API_BASE_URL}/health/`,
        },
      ];
    }
    // In production with different domains, return empty array (no rewrites)
    return [];
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
              // Image sources: production API + localhost for development
              `img-src 'self' data: blob: https: ${apiProtocol}://${apiHost}${apiUrlObj.port ? `:${apiUrlObj.port}` : ''}${process.env.NODE_ENV === 'development' ? ' http://localhost:8000 http://127.0.0.1:8000' : ''}`,
              "font-src 'self' data:",
              // Connect sources: production API + localhost for development
              `connect-src 'self' https://clerk.com https://*.clerk.com https://sound-mule-24.clerk.accounts.dev ${apiProtocol}://${apiHost}${apiUrlObj.port ? `:${apiUrlObj.port}` : ''}${process.env.NODE_ENV === 'development' ? ' http://localhost:8000 http://127.0.0.1:8000 ws://localhost:3000' : ''}`,
              "frame-src 'self' https://clerk.com https://*.clerk.com",
            ].join('; '),
          },
        ],
      },
    ]
  },
  // Improve chunk loading reliability
  webpack: (config, { isServer }) => {
    // Handle fabric.js and canvas for client-side only
    if (!isServer) {
      // Stub canvas module for client-side builds (fabric.js optional dependency)
      const path = require('path');
      config.resolve.alias = {
        ...config.resolve.alias,
        canvas: path.resolve(__dirname, 'webpack-canvas-stub.js'),
      };
      
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
    } else {
      // Server-side: stub canvas to prevent SSR errors
      config.resolve.alias = {
        ...config.resolve.alias,
        canvas: false,
      };
    }
    return config
  },
  // Add experimental features for better chunk loading
  experimental: {
    optimizePackageImports: ['@clerk/nextjs', '@clerk/themes'],
  },
};

export default nextConfig;
