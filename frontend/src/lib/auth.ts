/**
 * Authentication helper functions for JWT-based authentication
 */

import { buildApiUrl } from '@/utils/api'

const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'auth_user'

/**
 * Safely parse JSON response, checking for HTML error pages
 */
async function safeJsonParse(response: Response, url?: string): Promise<unknown> {
  const contentType = response.headers.get('content-type') || ''
  const text = await response.text()
  
  // Check if response looks like HTML
  const trimmedText = text.trim()
  if (trimmedText.startsWith('<!DOCTYPE') || trimmedText.startsWith('<html') || trimmedText.startsWith('<!')) {
    // Provide helpful debugging information
    const urlInfo = url ? ` URL: ${url}` : ''
    const preview = text.substring(0, 200).replace(/\n/g, ' ')
    
    // Check if it's Next.js index.html (common when rewrites fail)
    if (text.includes('__NEXT_DATA__') || text.includes('next.js')) {
      throw new Error(
        `Next.js served index.html instead of proxying to Django backend.${urlInfo}\n` +
        `This usually means:\n` +
        `1. The Django backend is not running on port 8000\n` +
        `2. Next.js rewrites are not working correctly\n` +
        `3. The API endpoint URL is incorrect\n` +
        `Response preview: ${preview}`
      )
    }
    
    throw new Error(
      `Backend returned HTML instead of JSON. Status: ${response.status}.${urlInfo}\n` +
      `Content-Type: ${contentType || 'not set'}\n` +
      `Response preview: ${preview}`
    )
  }
  
  // If empty, return empty object
  if (!text || text.trim() === '') {
    return {}
  }
  
  // Try to parse as JSON
  try {
    return JSON.parse(text)
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error(`Failed to parse JSON response: ${error.message}. The server may have returned HTML or an error page.`)
    }
    throw error
  }
}

// Token refresh mutex to prevent concurrent refresh attempts
let refreshPromise: Promise<boolean> | null = null

export interface User {
  id: string
  email: string
  username?: string
  first_name?: string
  last_name?: string
  phone_number?: string
  [key: string]: unknown
}

export interface AuthResponse {
  user?: User
  tokens?: {
    access: string
    refresh: string
  } | null
  email?: string
  message?: string
  requires_verification?: boolean
}

/**
 * Authentication error types
 */
export enum AuthErrorType {
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  NOT_VERIFIED = 'NOT_VERIFIED',
  SERVER_ERROR = 'SERVER_ERROR',
}

/**
 * Typed authentication error
 */
export class AuthError extends Error {
  type: AuthErrorType
  status: number
  email?: string
  requiresVerification?: boolean

  constructor(
    type: AuthErrorType,
    message: string,
    status: number,
    email?: string
  ) {
    super(message)
    this.name = 'AuthError'
    this.type = type
    this.status = status
    this.email = email
    if (type === AuthErrorType.NOT_VERIFIED) {
      this.requiresVerification = true
    }
  }
}

/**
 * Store authentication tokens in both localStorage and cookies
 */
export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window !== 'undefined') {
    // Store in localStorage for client-side access
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    
    // Also store in cookie for middleware access
    // Set cookie with 7 days expiry
    const expiryDate = new Date()
    expiryDate.setDate(expiryDate.getDate() + 7)
    
    document.cookie = `auth_token=${accessToken}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`
    document.cookie = `refresh_token=${refreshToken}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`
  }
}

/**
 * Get access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Get refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * Store user data
 */
export function setUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}

/**
 * Get user data from localStorage
 */
export function getUser(): User | null {
  if (typeof window === 'undefined') return null
  const userStr = localStorage.getItem(USER_KEY)
  if (!userStr) return null
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

/**
 * Clear all authentication data
 */
export function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    
    // Clear cookies
    document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
  }
}

/**
 * Get Django backend URL directly (bypasses Next.js rewrites)
 */
function getDjangoBackendUrl(): string {
  // In development, always use localhost:8000 directly
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000'
  }
  
  // In production, use environment variable or fallback
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/+$/, '')
  }
  
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '')
  }
  
  // Production fallback
  return 'http://13.213.53.199'
}

/**
 * Login with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  let response: Response
  
  // In development, use absolute URL to bypass Next.js rewrites
  // This ensures we hit Django directly even if rewrites aren't working
  const loginUrl = process.env.NODE_ENV === 'development' 
    ? `${getDjangoBackendUrl()}/api/users/auth/login/`
    : buildApiUrl('/api/users/auth/login/')
  
  try {
    response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })
  } catch (networkError) {
    // Network failure - unexpected error, log in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Login network error:', networkError)
    }
    throw new AuthError(
      AuthErrorType.SERVER_ERROR,
      'Network error. Please check your connection and try again.',
      0
    )
  }

  if (!response.ok) {
    // Handle expected user errors (401, 403) - don't log these
    if (response.status === 401) {
      throw new AuthError(
        AuthErrorType.INVALID_CREDENTIALS,
        'Invalid email or password',
        response.status
      )
    }

    if (response.status === 403) {
      // Check if it's a verification error
      let errorData: Record<string, unknown> = {}
      try {
        const text = await response.text()
        if (text && text.trim()) {
          try {
            errorData = JSON.parse(text)
          } catch {
            // Not valid JSON, ignore
          }
        }
      } catch {
        // Ignore parsing errors for expected user errors
      }

      const isVerificationError =
        (typeof errorData.requires_verification === 'boolean' && errorData.requires_verification) ||
        (typeof errorData.detail === 'string' && errorData.detail.toLowerCase().includes('verify'))

      if (isVerificationError) {
        const message =
          typeof errorData.detail === 'string'
            ? errorData.detail
            : 'Please verify your email address before logging in.'
        throw new AuthError(
          AuthErrorType.NOT_VERIFIED,
          message,
          response.status,
          typeof errorData.email === 'string' ? errorData.email : email
        )
      }

      throw new AuthError(
        AuthErrorType.NOT_VERIFIED,
        'Access forbidden',
        response.status
      )
    }

    // Handle unexpected server errors (5xx) - log these
    if (response.status >= 500) {
      let errorMessage = 'Server error. Please try again later.'
      try {
        const text = await response.text()
        if (text && text.trim()) {
          try {
            const errorData = JSON.parse(text)
            if (typeof errorData.detail === 'string' && errorData.detail.trim()) {
              errorMessage = errorData.detail
            } else if (typeof errorData.error === 'string' && errorData.error.trim()) {
              errorMessage = errorData.error
            }
          } catch {
            // Not valid JSON, use default message
          }
        }
      } catch {
        // Ignore parsing errors, use default message
      }

      if (process.env.NODE_ENV === 'development') {
        console.error('Login server error:', {
          status: response.status,
          message: errorMessage,
        })
      }

      throw new AuthError(AuthErrorType.SERVER_ERROR, errorMessage, response.status)
    }

    // Handle other unexpected errors (4xx except 401, 403)
    let errorMessage = `Login failed (${response.status})`
    try {
      const text = await response.text()
      if (text && text.trim()) {
        try {
          const errorData = JSON.parse(text)
          if (typeof errorData.detail === 'string' && errorData.detail.trim()) {
            errorMessage = errorData.detail
          } else if (typeof errorData.error === 'string' && errorData.error.trim()) {
            errorMessage = errorData.error
          } else if (typeof errorData.message === 'string' && errorData.message.trim()) {
            errorMessage = errorData.message
          }
        } catch (parseError) {
          // JSON parsing failed - unexpected error, log in development
          if (process.env.NODE_ENV === 'development') {
            console.error('Login error response parsing failed:', parseError, {
              status: response.status,
              responseText: text.substring(0, 200),
            })
          }
        }
      }
    } catch (readError) {
      // Response reading failed - unexpected error, log in development
      if (process.env.NODE_ENV === 'development') {
        console.error('Login error response read failed:', readError, {
          status: response.status,
        })
      }
    }

    if (process.env.NODE_ENV === 'development') {
      console.error('Login unexpected error:', {
        status: response.status,
        message: errorMessage,
      })
    }

    throw new AuthError(AuthErrorType.SERVER_ERROR, errorMessage, response.status)
  }

  // Success - parse response
  let responseData: unknown
  try {
    responseData = await safeJsonParse(response, loginUrl)
  } catch (parseError) {
    // JSON parsing failed on success response - unexpected error, log in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Login success response parsing failed:', parseError)
    }
    throw new AuthError(
      AuthErrorType.SERVER_ERROR,
      'Invalid response from server. Please try again.',
      response.status
    )
  }

  // Handle response data - API may return tokens at top level or nested
  const data = responseData as Record<string, unknown>
  const accessToken = (data.access as string) || (data.tokens as { access?: string })?.access
  const refreshToken = (data.refresh as string) || (data.tokens as { refresh?: string })?.refresh
  const user = data.user as User | undefined

  // Store tokens and user
  if (accessToken && refreshToken) {
    setTokens(accessToken, refreshToken)
  }

  if (user) {
    setUser(user)
  }

  const result: AuthResponse = {
    user: user,
    tokens: accessToken && refreshToken ? { access: accessToken, refresh: refreshToken } : undefined,
  }

  return result
}

/**
 * Register a new user
 */
export async function register(
  username: string,
  email: string,
  password: string,
  firstName?: string,
  lastName?: string
): Promise<AuthResponse> {
  // Build request body, only including defined values
  const body: Record<string, string> = {
    username,
    email,
    password,
  }
  
  if (firstName) {
    body.first_name = firstName
  }
  
  if (lastName) {
    body.last_name = lastName
  }

  const response = await fetch(buildApiUrl('/api/users/auth/register/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const errorData = await safeJsonParse(response).catch(() => ({ error: 'Registration failed' })) as { error?: string; detail?: string; details?: string[] }
    // Include details if available (e.g., password validation errors)
    const errorMessage = errorData.error || errorData.detail || 'Registration failed'
    const details = errorData.details ? ` ${errorData.details.join(', ')}` : ''
    throw new Error(errorMessage + details)
  }

  const data = await safeJsonParse(response) as AuthResponse & {
    requires_verification?: boolean
    tokens?: { access: string; refresh: string } | null
    user?: User
    email?: string
    message?: string
  }
  
  // Check if verification is required (strict mode - no tokens returned)
  if (data.requires_verification && !data.tokens) {
    // Don't store tokens - user must verify email first
    return {
      user: data.user,
      email: data.email || data.user?.email,
      message: data.message,
      requires_verification: true,
      tokens: undefined, // Explicitly no tokens
    }
  }
  
  // Store tokens and user only if verification not required
  if (data.tokens?.access && data.tokens?.refresh) {
    setTokens(data.tokens.access, data.tokens.refresh)
  }
  
  if (data.user) {
    setUser(data.user)
  }

  return data
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken()
  
  if (refreshToken) {
    try {
      const accessToken = getAccessToken()
      await fetch(buildApiUrl('/api/users/auth/logout/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      })
    } catch (error) {
      console.warn('Logout API call failed:', error)
    }
  }
  
  clearAuth()
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(retryCount = 0): Promise<User | null> {
  const accessToken = getAccessToken()
  
  if (!accessToken) {
    return getUser() // Return cached user if no token
  }

  try {
    const response = await fetch(buildApiUrl('/api/users/auth/me/'), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      // Check content type before parsing JSON
      const contentType = response.headers.get('content-type') || ''
      const isJson = contentType.includes('application/json')
      
      if (isJson) {
        try {
          const data = await response.json()
          const user = data.user || data
          setUser(user)
          return user
        } catch (jsonError) {
          // JSON parsing failed - might be HTML error page
          const text = await response.text().catch(() => '')
          if (process.env.NODE_ENV === 'development') {
            console.warn('Failed to parse JSON response from /api/users/auth/me:', jsonError, {
              contentType,
              preview: text.substring(0, 200)
            })
          }
          return getUser() // Fallback to cached user
        }
      } else {
        // Not JSON response - likely HTML error page
        if (process.env.NODE_ENV === 'development') {
          const text = await response.text().catch(() => '')
          console.warn('Backend returned non-JSON response:', {
            contentType,
            preview: text.substring(0, 200)
          })
        }
        return getUser() // Fallback to cached user
      }
    } else if (response.status === 401 && retryCount === 0) {
      // Token expired, try to refresh (only retry once to prevent infinite recursion)
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Retry with new token (increment retry count)
        return getCurrentUser(retryCount + 1)
      }
      clearAuth()
      return null
    }
    
    return getUser() // Fallback to cached user
  } catch (error) {
    console.warn('Failed to fetch current user:', error)
    return getUser() // Fallback to cached user
  }
}

/**
 * Refresh access token using refresh token
 * Uses a mutex to prevent concurrent refresh attempts
 */
export async function refreshAccessToken(): Promise<boolean> {
  // If a refresh is already in progress, wait for it instead of starting a new one
  if (refreshPromise) {
    return refreshPromise
  }

  const refreshToken = getRefreshToken()
  
  if (!refreshToken) {
    return false
  }

  // Create the refresh promise and store it
  refreshPromise = (async (): Promise<boolean> => {
    try {
      const response = await fetch(buildApiUrl('/api/users/auth/token/refresh/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      })

      if (response.ok) {
        const data = await safeJsonParse(response) as { access?: string }
        if (data.access) {
          // Update both localStorage and cookies
          const currentRefreshToken = getRefreshToken()
          setTokens(data.access, currentRefreshToken || refreshToken)
          return true
        }
      } else {
        // If refresh fails, clear auth to force re-login
        const errorData = await safeJsonParse(response).catch(() => ({})) as { detail?: string }
        if (errorData.detail?.includes('blacklisted') || errorData.detail?.includes('expired')) {
          console.warn('Refresh token is invalid, clearing auth')
          clearAuth()
        }
      }
      
      return false
    } catch (error) {
      console.warn('Failed to refresh token:', error)
      return false
    } finally {
      // Clear the promise so future calls can start a new refresh
      refreshPromise = null
    }
  })()

  return refreshPromise
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken()
}

/**
 * Get authorization header for API requests
 */
export function getAuthHeader(): string | null {
  const token = getAccessToken()
  return token ? `Bearer ${token}` : null
}

/**
 * Send verification email
 */
export async function sendVerificationEmail(email: string): Promise<void> {
  const response = await fetch(buildApiUrl('/api/users/auth/send-verification-email/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  })

  if (!response.ok) {
    const error = await safeJsonParse(response).catch(() => ({ error: 'Failed to send verification email' })) as { error?: string; message?: string }
    throw new Error(error.error || error.message || 'Failed to send verification email')
  }
}

/**
 * Check verification status
 */
export async function checkVerificationStatus(): Promise<{ is_verified: boolean; email: string }> {
  const accessToken = getAccessToken()
  
  if (!accessToken) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(buildApiUrl('/api/users/auth/verification-status/'), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error = await safeJsonParse(response).catch(() => ({ error: 'Failed to check verification status' })) as { error?: string; message?: string }
    throw new Error(error.error || error.message || 'Failed to check verification status')
  }

  return safeJsonParse(response) as Promise<{ is_verified: boolean; email: string }>
}

/**
 * Verify email with token
 */
export async function verifyEmail(token: string): Promise<{ message: string; user: User; access?: string; refresh?: string }> {
  const response = await fetch(buildApiUrl(`/api/users/auth/verify-email/${token}/`), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error = await safeJsonParse(response).catch(() => ({ error: 'Failed to verify email' })) as { error?: string; message?: string }
    throw new Error(error.error || error.message || 'Failed to verify email')
  }

  const data = await safeJsonParse(response) as {
    message: string
    user: User
    access?: string
    refresh?: string
  }
  
  // Update user data if verification successful (tokens will be set via server-side route)
  if (data.user) {
    setUser(data.user)
  }

  return data
}

