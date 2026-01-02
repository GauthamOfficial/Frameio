/**
 * Rate limiting utilities for API routes
 * Prevents abuse and brute force attacks
 */

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

// In-memory store (for production, use Redis or similar)
const rateLimitStore: RateLimitStore = {};

// Clean up expired entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  Object.keys(rateLimitStore).forEach(key => {
    if (rateLimitStore[key].resetTime < now) {
      delete rateLimitStore[key];
    }
  });
}, 5 * 60 * 1000);

/**
 * Get client identifier from request
 */
function getClientId(request: Request): string {
  // Try to get IP from various headers (behind proxy)
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');
  const ip = forwarded?.split(',')[0] || realIp || 'unknown';
  
  // Also use user agent for additional identification
  const userAgent = request.headers.get('user-agent') || 'unknown';
  
  return `${ip}:${userAgent}`;
}

export interface RateLimitOptions {
  windowMs: number; // Time window in milliseconds
  maxRequests: number; // Maximum requests per window
  message?: string; // Custom error message
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetTime: number;
  retryAfter?: number;
}

/**
 * Check rate limit for a request
 */
export function checkRateLimit(
  request: Request,
  options: RateLimitOptions
): RateLimitResult {
  const clientId = getClientId(request);
  const now = Date.now();
  
  // Get or create rate limit entry
  let entry = rateLimitStore[clientId];
  
  if (!entry || entry.resetTime < now) {
    // Create new entry or reset expired one
    entry = {
      count: 0,
      resetTime: now + options.windowMs,
    };
    rateLimitStore[clientId] = entry;
  }
  
  // Increment count
  entry.count++;
  
  const remaining = Math.max(0, options.maxRequests - entry.count);
  const allowed = entry.count <= options.maxRequests;
  
  return {
    allowed,
    remaining,
    resetTime: entry.resetTime,
    retryAfter: allowed ? undefined : Math.ceil((entry.resetTime - now) / 1000),
  };
}

/**
 * Rate limit middleware for Next.js API routes
 */
export function withRateLimit(
  handler: (request: Request) => Promise<Response>,
  options: RateLimitOptions
) {
  return async (request: Request): Promise<Response> => {
    const result = checkRateLimit(request, options);
    
    if (!result.allowed) {
      return new Response(
        JSON.stringify({
          error: options.message || 'Too many requests',
          retryAfter: result.retryAfter,
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': String(result.retryAfter || 60),
            'X-RateLimit-Limit': String(options.maxRequests),
            'X-RateLimit-Remaining': String(result.remaining),
            'X-RateLimit-Reset': String(result.resetTime),
          },
        }
      );
    }
    
    // Add rate limit headers to response
    const response = await handler(request);
    const headers = new Headers(response.headers);
    headers.set('X-RateLimit-Limit', String(options.maxRequests));
    headers.set('X-RateLimit-Remaining', String(result.remaining));
    headers.set('X-RateLimit-Reset', String(result.resetTime));
    
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  };
}

/**
 * Predefined rate limit configurations
 */
export const RateLimitPresets = {
  // Strict: 5 requests per minute
  strict: {
    windowMs: 60 * 1000,
    maxRequests: 5,
    message: 'Too many requests. Please try again later.',
  },
  
  // Standard: 100 requests per 15 minutes
  standard: {
    windowMs: 15 * 60 * 1000,
    maxRequests: 100,
    message: 'Too many requests. Please try again later.',
  },
  
  // Auth endpoints: 5 requests per minute
  auth: {
    windowMs: 60 * 1000,
    maxRequests: 5,
    message: 'Too many authentication attempts. Please try again later.',
  },
  
  // API endpoints: 1000 requests per hour
  api: {
    windowMs: 60 * 60 * 1000,
    maxRequests: 1000,
    message: 'API rate limit exceeded. Please try again later.',
  },
};

