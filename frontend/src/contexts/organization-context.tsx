"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useUser, useAuth } from '@clerk/nextjs'
import { userApi, testApi } from '@/lib/api'
import { useApp } from './app-context'

export type UserRole = 'Designer' | 'Admin'

export interface OrganizationContextType {
  organizationId: string | null
  userRole: UserRole | null
  permissions: string[]
  isLoading: boolean
  error: string | null
  refreshUserData: () => Promise<void>
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined)

interface OrganizationProviderProps {
  children: React.ReactNode
}

export function OrganizationProvider({ children }: OrganizationProviderProps) {
  const { user, isLoaded } = useUser()
  const { getToken } = useAuth()
  const { setGlobalLoading, setError: setAppError } = useApp()
  const [organizationId, setOrganizationId] = useState<string | null>(null)
  const [userRole, setUserRole] = useState<UserRole | null>(null)
  const [permissions, setPermissions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUserProfile = async () => {
    if (!user || !isLoaded) return

    try {
      setIsLoading(true)
      setGlobalLoading(true)
      setError(null)

      // Check if we're in a test environment or have localStorage data
      const testRole = typeof window !== 'undefined' ? localStorage.getItem('user-role') : null
      const testOrgId = typeof window !== 'undefined' ? localStorage.getItem('organization-id') : null
      const testOrgName = typeof window !== 'undefined' ? localStorage.getItem('organization-name') : null
      const testPermissions = typeof window !== 'undefined' ? localStorage.getItem('user-permissions') : null

      console.log('Organization Context Debug:', { testRole, testOrgId, testOrgName, testPermissions })

      // For development, set up test data if not already present
      if (!testRole && !testOrgId) {
        console.log('Setting up test data for development')
        if (typeof window !== 'undefined') {
          localStorage.setItem('user-role', 'Designer')
          localStorage.setItem('organization-id', '0a4e8956-b626-4ac5-b082-b13febeb5bfe')
          localStorage.setItem('organization-name', 'Test Organization')
          localStorage.setItem('dev-user-id', '96e65d2a-9139-404e-b8c8-582d5a3ff525')
          localStorage.setItem('dev-org-id', '0a4e8956-b626-4ac5-b082-b13febeb5bfe')
          localStorage.setItem('user-permissions', JSON.stringify([
            'manage_designs',
            'view_templates',
            'view_analytics'
          ]))
        }
      }

      if (testRole && testOrgId) {
        // Use test data from localStorage
        console.log('Using test data from localStorage')
        setOrganizationId(testOrgId)
        setUserRole(testRole as UserRole)
        setPermissions(testPermissions ? JSON.parse(testPermissions) : [])
        setIsLoading(false)
        return
      }

      // Test backend connectivity first
      console.log('Testing backend connectivity...')
      try {
        const healthCheck = await testApi.healthCheck()
        console.log('Backend health check:', healthCheck)
      } catch (healthError) {
        console.error('Backend health check failed:', healthError)
        throw new Error('Backend server is not accessible')
      }

      // Get user profile from backend
      console.log('Fetching user profile from backend')
      const token = await getToken()
      console.log('Got token:', token ? 'Yes' : 'No')
      
      if (!token) {
        throw new Error('No authentication token available')
      }

      try {
        const userProfile = await userApi.getProfile(token)
        console.log('User profile:', userProfile)
        
        // Extract organization and role from the profile
        const organizationId = userProfile.current_organization
        const userRole = userProfile.user_role || 'Designer' // Default role if not specified
        
        setOrganizationId(organizationId)
        setUserRole(userRole as UserRole)
        
        // Set permissions based on role
        const rolePermissions = getRolePermissions(userRole as UserRole)
        console.log('Role permissions:', rolePermissions)
        setPermissions(rolePermissions)
        
      } catch (profileError: any) {
        console.error('Profile fetch error:', profileError)
        
        // Handle specific profile errors
        if (profileError.response?.status === 403) {
          throw new Error('User is not part of any organization. Please contact an administrator to be added to an organization.')
        } else if (profileError.response?.status === 401) {
          throw new Error('Authentication failed. Please log in again.')
        } else {
          throw profileError
        }
      }

    } catch (err: any) {
      console.error('Failed to fetch user profile:', err)
      
      // Handle specific error types
      if (err.message?.includes('Network Error') || err.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check if the backend is running.')
      } else if (err.response?.status === 401) {
        setError('Authentication failed. Please log in again.')
      } else if (err.response?.status === 403) {
        setError('Access denied. You may not have permission to access this organization.')
      } else if (err.response?.status === 404) {
        setError('User profile not found. Please contact support.')
      } else {
        setError(`Failed to load user data: ${err.message || 'Unknown error'}`)
      }
      
      // Set default permissions for testing if backend fails
      console.log('Setting default permissions for testing')
      setUserRole('Designer')
      setPermissions(['manage_designs', 'view_templates', 'view_analytics'])
    } finally {
      setIsLoading(false)
      setGlobalLoading(false)
    }
  }

  const getRolePermissions = (role: UserRole): string[] => {
    switch (role) {
      case 'Designer':
        return [
          'manage_designs',
          'view_templates',
          'view_analytics'
        ]
      case 'Admin':
        return [
          'admin_access',
          'manage_users',
          'manage_organizations',
          'manage_designs',
          'view_templates',
          'view_analytics'
        ]
      default:
        return []
    }
  }

  const refreshUserData = async () => {
    await fetchUserProfile()
  }

  useEffect(() => {
    if (isLoaded && user) {
      fetchUserProfile()
    }
  }, [user, isLoaded])

  const value: OrganizationContextType = {
    organizationId,
    userRole,
    permissions,
    isLoading,
    error,
    refreshUserData
  }

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  )
}

export function useOrganization() {
  const context = useContext(OrganizationContext)
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider')
  }
  return context
}
