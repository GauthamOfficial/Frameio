import type { NextConfig } from "next";
import path from "path";

// Get API base URL from environment, with fallback for development
const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/+$/, "");
    return base.endsWith("/api") ? base : `${base}/api`;
  }

  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }

  return "https://frameio.co/api";
};

const API_BASE_URL = getApiBaseUrl();
const apiUrlObj = new URL(API_BASE_URL);
const apiHost = apiUrlObj.hostname;
const apiProtocol = apiUrlObj.protocol.slice(0, -1);

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname),

  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        pathname: "/**",
      },
      {
        protocol: "http",
        hostname: "127.0.0.1",
        pathname: "/**",
      },
      ...(apiHost !== "localhost" && apiHost !== "127.0.0.1"
        ? [
            {
              protocol: apiProtocol as "http" | "https",
              hostname: apiHost,
              ...(apiUrlObj.port ? { port: apiUrlObj.port } : {}),
              pathname: "/**",
            },
          ]
        : []),
      {
        protocol: "https",
        hostname: "*.ngrok.io",
        pathname: "/media/**",
      },
    ],
  },

  experimental: {
    optimizePackageImports: ["@clerk/nextjs", "@clerk/themes"],
  },

  async rewrites() {
    if (
      process.env.NODE_ENV === "development" ||
      apiHost === "localhost" ||
      apiHost === "127.0.0.1"
    ) {
      return [
        {
          source: "/api/ai/:path*",
          destination: `${API_BASE_URL}/api/ai/:path*`,
        },
        {
          source: "/api/((?!admin|users/auth/me|users/me|auth/set-tokens).*)",
          destination: `${API_BASE_URL}/api/$1`,
        },
        {
          source: "/health",
          destination: `${API_BASE_URL}/health/`,
        },
      ];
    }
    return [];
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              process.env.NODE_ENV === "development"
                ? "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
                : "script-src 'self' 'unsafe-inline'",
              "worker-src 'self' blob:",
              "child-src 'self' blob:",
              "style-src 'self' 'unsafe-inline'",
              `img-src 'self' data: blob: https: ${apiProtocol}://${apiHost}${
                apiUrlObj.port ? `:${apiUrlObj.port}` : ""
              }${
                apiHost === "localhost" || apiHost === "127.0.0.1"
                  ? " http://localhost:8000 http://127.0.0.1:8000"
                  : ""
              }`,
              "font-src 'self' data:",
              `connect-src 'self' ${apiProtocol}://${apiHost}${
                apiUrlObj.port ? `:${apiUrlObj.port}` : ""
              }${
                apiHost === "localhost" || apiHost === "127.0.0.1"
                  ? " http://localhost:8000 http://127.0.0.1:8000 ws://localhost:3000"
                  : ""
              }`,
              "frame-src 'self'",
            ].join("; "),
          },
        ],
      },
    ];
  },

  webpack: (config, { isServer }) => {
    if (!isServer) {
      const path = require("path");
      config.resolve.alias = {
        ...config.resolve.alias,
        canvas: path.resolve(__dirname, "webpack-canvas-stub.js"),
      };
    } else {
      config.resolve.alias = {
        ...config.resolve.alias,
        canvas: false,
      };
    }
    return config;
  },

  // Turbopack enabled (safe with existing experimental config)
  turbopack: {},
};

export default nextConfig;
