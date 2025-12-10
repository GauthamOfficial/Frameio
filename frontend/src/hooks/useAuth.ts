"use client"

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { 
  getCurrentUser, 
  logout as authLogout, 
  isAuthenticated,
  getAccessToken,
  type User 
} from '@/lib/auth'
import { buildApiUrl } from '@/utils/api'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  token: string | null
}

export function useAuth() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    token: null,
  })

  const fetchUser = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }))
      
      const token = getAccessToken()
      if (!token || !isAuthenticated()) {
        setAuthState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          token: null,
        })
        return
      }

      const user = await getCurrentUser()
      setAuthState({
        user,
        isLoading: false,
        isAuthenticated: !!user,
        token,
      })
    } catch (error) {
      console.error('Auth error:', error)
      setAuthState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        token: null,
      })
    }
  }, [])

  useEffect(() => {
    fetchUser()

    // Listen for storage changes (when token is set in another tab/window)
    const handleStorageChange = () => {
      fetchUser()
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [fetchUser])

  const getToken = useCallback(async (): Promise<string | null> => {
    return getAccessToken()
  }, [])

  const signOut = useCallback(async () => {
    try {
      await authLogout()
    } catch (error) {
      console.warn('Logout error:', error)
    }
    
    setAuthState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      token: null,
    })
    
    router.push('/sign-in')
  }, [router])

  return {
    user: authState.user,
    userId: authState.user?.id || null,
    isLoaded: !authState.isLoading,
    isLoading: authState.isLoading,
    isSignedIn: authState.isAuthenticated,
    isAuthenticated: authState.isAuthenticated,
    getToken,
    signOut,
  }
}

// Alias for useUser compatibility
export function useUser() {
  const auth = useAuth()
  
  return {
    user: auth.user,
    isLoaded: auth.isLoaded,
    isSignedIn: auth.isSignedIn,
  }
}
