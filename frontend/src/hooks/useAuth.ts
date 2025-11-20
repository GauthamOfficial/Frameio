"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth as useClerkAuth, useUser as useClerkUser } from '@clerk/nextjs'

interface User {
  id: string
  email: string
  username?: string
  [key: string]: any
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  token: string | null
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Auth hook that integrates with Clerk
export function useAuth() {
  const clerkAuth = useClerkAuth()
  const { user: clerkUser, isLoaded: clerkLoaded } = useClerkUser()
  
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    token: null,
  })

  // Use refs to track previous values and prevent infinite loops
  const fetchingRef = useRef(false)
  const lastClerkUserIdRef = useRef<string | null>(null)

  // Get token - use Clerk's getToken or fallback to test token in development
  const getToken = useCallback(async (): Promise<string | null> => {
    // Try to get Clerk token first
    if (clerkAuth.getToken) {
      try {
        const clerkToken = await clerkAuth.getToken()
        if (clerkToken) {
          return clerkToken
        }
      } catch (error) {
        console.warn('Failed to get Clerk token:', error)
      }
    }
    
    // Check localStorage for stored token
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      return storedToken
    }
    
    // In development, fallback to test token
    if (process.env.NODE_ENV === 'development') {
      return 'test_clerk_token'
    }
    
    return null
  }, [clerkAuth])

  // Fetch user data
  const fetchUser = useCallback(async () => {
    // Prevent multiple simultaneous calls
    if (fetchingRef.current) {
      return
    }

    try {
      fetchingRef.current = true

      // If Clerk user is available, use it
      if (clerkUser && clerkLoaded) {
        const token = await getToken()
        setAuthState({
          user: {
            id: clerkUser.id,
            email: clerkUser.emailAddresses?.[0]?.emailAddress || '',
            username: clerkUser.username || clerkUser.firstName || '',
          },
          isLoading: false,
          isAuthenticated: true,
          token,
        })
        lastClerkUserIdRef.current = clerkUser.id
        return
      }
      
      // Otherwise, try to fetch from backend
      const token = await getToken()
      if (!token) {
        setAuthState({
          user: null,
          isLoading: !clerkLoaded, // Still loading if Clerk is not loaded yet
          isAuthenticated: false,
          token: null,
        })
        return
      }

      const response = await fetch(`${API_BASE_URL}/api/users/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        const user = Array.isArray(data) ? data[0] : data
        setAuthState({
          user,
          isLoading: false,
          isAuthenticated: true,
          token,
        })
      } else {
        setAuthState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          token: null,
        })
      }
    } catch (error) {
      console.error('Auth error:', error)
      setAuthState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        token: null,
      })
    } finally {
      fetchingRef.current = false
    }
  }, [getToken, clerkUser?.id, clerkLoaded])

  useEffect(() => {
    // Only fetch if Clerk user ID changed or if Clerk just loaded
    const currentClerkUserId = clerkUser?.id || null
    const userIdChanged = currentClerkUserId !== lastClerkUserIdRef.current
    
    if ((userIdChanged || !clerkLoaded) && !fetchingRef.current) {
      fetchUser()
    }
    
    // Listen for storage changes (when token is set in another tab/window)
    const handleStorageChange = () => {
      if (!fetchingRef.current) {
        fetchUser()
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clerkLoaded, clerkUser?.id])

  const signOut = useCallback(async () => {
    // Sign out from Clerk if available
    if (clerkAuth.signOut) {
      try {
        await clerkAuth.signOut()
      } catch (error) {
        console.warn('Failed to sign out from Clerk:', error)
      }
    }
    
    // Clear local storage
    localStorage.removeItem('auth_token')
    
    setAuthState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      token: null,
    })
  }, [clerkAuth])

  return {
    user: authState.user,
    userId: authState.user?.id || null,
    isLoaded: clerkLoaded && !authState.isLoading,
    isLoading: !clerkLoaded || authState.isLoading,
    isSignedIn: authState.isAuthenticated,
    isAuthenticated: authState.isAuthenticated,
    getToken,
    signOut,
  }
}

// Alias for useUser compatibility - returns Clerk user format
export function useUser() {
  const { user: clerkUser, isLoaded: clerkLoaded } = useClerkUser()
  const auth = useAuth()
  
  // Prefer Clerk user if available
  if (clerkUser && clerkLoaded) {
    return {
      user: clerkUser,
      isLoaded: clerkLoaded,
      isSignedIn: !!clerkUser,
    }
  }
  
  // Fallback to custom auth
  return {
    user: auth.user,
    isLoaded: auth.isLoaded,
    isSignedIn: auth.isSignedIn,
  }
}

