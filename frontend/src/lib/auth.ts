/**
 * Authentication helper functions for JWT-based authentication
 */

import { buildApiUrl } from '@/utils/api'

const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'auth_user'

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
 * Login with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(buildApiUrl('/api/users/auth/login/'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Login failed' }))
    console.error('Login error response:', error)
    
    // Check if error is about email verification
    if (response.status === 403 && (error.requires_verification || error.detail?.toLowerCase().includes('verify'))) {
      const errorMessage = error.detail || error.error || 'Please verify your email address before logging in.'
      const verificationError = new Error(errorMessage) as Error & { requiresVerification?: boolean; email?: string }
      verificationError.requiresVerification = true
      verificationError.email = error.email
      throw verificationError
    }
    
    // Extract error message - prefer detail field as it has the specific reason
    const errorMessage = error.detail || error.error || error.message || 'Login failed'
    throw new Error(errorMessage)
  }

  const data = await response.json()
  
  // Store tokens and user
  if (data.access && data.refresh) {
    setTokens(data.access, data.refresh)
  } else if (data.tokens?.access && data.tokens?.refresh) {
    setTokens(data.tokens.access, data.tokens.refresh)
  }
  
  if (data.user) {
    setUser(data.user)
  }

  return {
    user: data.user || data,
    tokens: {
      access: data.access || data.tokens?.access,
      refresh: data.refresh || data.tokens?.refresh,
    },
  }
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
    const errorData = await response.json().catch(() => ({ error: 'Registration failed' }))
    // Include details if available (e.g., password validation errors)
    const errorMessage = errorData.error || errorData.detail || 'Registration failed'
    const details = errorData.details ? ` ${errorData.details.join(', ')}` : ''
    throw new Error(errorMessage + details)
  }

  const data = await response.json()
  
  // Check if verification is required (strict mode - no tokens returned)
  if (data.requires_verification && !data.tokens) {
    // Don't store tokens - user must verify email first
    return {
      user: data.user || { email: data.email },
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
export async function getCurrentUser(): Promise<User | null> {
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
      const data = await response.json()
      const user = data.user || data
      setUser(user)
      return user
    } else if (response.status === 401) {
      // Token expired, try to refresh
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Retry with new token
        return getCurrentUser()
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
 */
export async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  
  if (!refreshToken) {
    return false
  }

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
      const data = await response.json()
      if (data.access) {
        localStorage.setItem(TOKEN_KEY, data.access)
        return true
      }
    }
    
    return false
  } catch (error) {
    console.warn('Failed to refresh token:', error)
    return false
  }
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
    const error = await response.json().catch(() => ({ error: 'Failed to send verification email' }))
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
    const error = await response.json().catch(() => ({ error: 'Failed to check verification status' }))
    throw new Error(error.error || error.message || 'Failed to check verification status')
  }

  return response.json()
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
    const error = await response.json().catch(() => ({ error: 'Failed to verify email' }))
    throw new Error(error.error || error.message || 'Failed to verify email')
  }

  const data = await response.json()
  
  // Update user data if verification successful (tokens will be set via server-side route)
  if (data.user) {
    setUser(data.user)
  }

  return data
}

