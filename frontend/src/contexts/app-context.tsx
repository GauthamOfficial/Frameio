"use client"

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react'
import { useUser, useAuth } from '@/hooks/useAuth'
import { setAuthToken } from '@/lib/api'
// Removed circular dependency - toast helpers will be used directly in components

export interface AppState {
  // Auth state
  isAuthenticated: boolean
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  user: any
  token: string | null
  
  // Organization state
  organizationId: string | null
  userRole: string | null
  permissions: string[]
  
  // UI state
  isLoading: boolean
  isGlobalLoading: boolean
  error: string | null
  
  // Actions
  setGlobalLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  refreshAuth: () => Promise<void>
  logout: () => void
}

const AppContext = createContext<AppState | undefined>(undefined)

interface AppProviderProps {
  children: React.ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const { user, isLoaded: userLoaded } = useUser()
  const { getToken, signOut } = useAuth()
  
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState<string | null>(null)
  
  // Organization state
  const [organizationId, setOrganizationId] = useState<string | null>(null)
  const [userRole, setUserRole] = useState<string | null>(null)
  const [permissions, setPermissions] = useState<string[]>([])
  
  // UI state
  const [isLoading, setIsLoading] = useState(true)
  const [isGlobalLoading, setIsGlobalLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Use refs to track previous values and prevent infinite loops
  const initializingRef = useRef(false)
  const lastUserIdRef = useRef<string | null>(null)

  // Initialize auth state
  const initializeAuth = useCallback(async () => {
    if (!userLoaded || initializingRef.current) return

    const currentUserId = user?.id || null
    // Only initialize if user ID changed
    if (currentUserId === lastUserIdRef.current) {
      return
    }

    try {
      initializingRef.current = true
      setIsLoading(true)
      
      if (user) {
        const authToken = await getToken()
        if (authToken) {
          setToken(authToken)
          setAuthToken(authToken)
          setIsAuthenticated(true)
          
          // Load organization data from localStorage for development
          const storedOrgId = localStorage.getItem('organization-id')
          const storedRole = localStorage.getItem('user-role')
          const storedPermissions = localStorage.getItem('user-permissions')
          
          if (storedOrgId && storedRole) {
            setOrganizationId(storedOrgId)
            setUserRole(storedRole)
            setPermissions(storedPermissions ? JSON.parse(storedPermissions) : [])
          }
          
          // Store token in localStorage for development
          localStorage.setItem('auth-token', authToken)
        }
        lastUserIdRef.current = currentUserId
      } else {
        setIsAuthenticated(false)
        setToken(null)
        setAuthToken(null)
        setOrganizationId(null)
        setUserRole(null)
        setPermissions([])
        lastUserIdRef.current = null
      }
    } catch (err: unknown) {
      console.error('Auth initialization error:', err)
      setError('Failed to initialize authentication')
    } finally {
      setIsLoading(false)
      initializingRef.current = false
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, userLoaded, getToken])

  // Refresh auth state
  const refreshAuth = useCallback(async () => {
    await initializeAuth()
  }, [initializeAuth])

  // Logout function
  const logout = useCallback(async () => {
    try {
      setIsGlobalLoading(true)
      await signOut()
      setToken(null)
      setAuthToken(null)
      setIsAuthenticated(false)
      setOrganizationId(null)
      setUserRole(null)
      setPermissions([])
      setError(null)
      
      // Clear localStorage
      localStorage.removeItem('organization-id')
      localStorage.removeItem('user-role')
      localStorage.removeItem('user-permissions')
      localStorage.removeItem('dev-user-id')
      localStorage.removeItem('dev-org-id')
      localStorage.removeItem('auth-token')
      
      console.log('Logged out successfully')
    } catch (err: unknown) {
      console.error('Logout error:', err)
      console.error('Failed to log out')
    } finally {
      setIsGlobalLoading(false)
    }
  }, [signOut])

  // Clear error function
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Set global loading
  const setGlobalLoading = useCallback((loading: boolean) => {
    setIsGlobalLoading(loading)
  }, [])

  // Set error function
  const setErrorWithToast = useCallback((errorMessage: string | null) => {
    setError(errorMessage)
    if (errorMessage) {
      console.error('App Error:', errorMessage)
    }
  }, [])

  // Initialize auth on mount and when user changes
  useEffect(() => {
    initializeAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userLoaded, user?.id])

  // Listen for API errors
  useEffect(() => {
    const handleApiError = (event: CustomEvent) => {
      const { type, message } = event.detail
      
      switch (type) {
        case 'unauthorized':
          setError(message)
          // Don't auto-logout, let user handle it
          break
        case 'network':
          setError(message)
          break
        case 'server':
          setError(message)
          break
        case 'forbidden':
          setError(message)
          break
        default:
          setError(message)
      }
    }

    window.addEventListener('api-error', handleApiError as EventListener)
    
    return () => {
      window.removeEventListener('api-error', handleApiError as EventListener)
    }
  }, [])

  const value: AppState = {
    // Auth state
    isAuthenticated,
    user,
    token,
    
    // Organization state
    organizationId,
    userRole,
    permissions,
    
    // UI state
    isLoading,
    isGlobalLoading,
    error,
    
    // Actions
    setGlobalLoading,
    setError: setErrorWithToast,
    clearError,
    refreshAuth,
    logout,
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

// Export as useAppContext for backward compatibility
export const useAppContext = useApp