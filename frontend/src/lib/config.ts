/**
 * Application configuration
 */

// API Configuration
// Default to localhost:8000 if not set in environment
const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const API_BASE_URL = baseUrl.replace(/\/$/, '')

// Helper function to build API endpoints
// Uses relative URLs if API_BASE_URL is not set (for Next.js proxy)
const buildEndpoint = (path: string): string => {
  if (API_BASE_URL) {
    return `${API_BASE_URL}${path}`
  }
  // Use relative URL for Next.js proxy
  return path
}

// API Endpoints
export const API_ENDPOINTS = {
  // User endpoints - FIXED: Backend has company-profiles at /api/company-profiles/ NOT /api/users/company-profiles/
  COMPANY_PROFILES: buildEndpoint('/api/company-profiles/'),
  COMPANY_PROFILES_STATUS: buildEndpoint('/api/company-profiles/status/'),
  
  // AI endpoints
  AI_POSTER_GENERATE: buildEndpoint('/api/ai/ai-poster/generate_poster/'),
  AI_POSTER_EDIT: buildEndpoint('/api/ai/ai-poster/edit_poster/'),
  AI_POSTER_STATUS: buildEndpoint('/api/ai/ai-poster/status/'),
} as const

