import axios, { AxiosError, AxiosResponse } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Token management
let authToken: string | null = null

export const setAuthToken = (token: string | null) => {
  authToken = token
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

export const getAuthToken = () => authToken

// Add request interceptor for error handling
api.interceptors.request.use(
  (config) => {
    console.log(`Making API request to: ${config.baseURL}${config.url}`)
    
    // Add development headers for testing
    if (typeof window !== 'undefined') {
      const devUserId = localStorage.getItem('dev-user-id')
      const devOrgId = localStorage.getItem('dev-org-id')
      
      if (devUserId && devOrgId) {
        config.headers['X-Dev-User-ID'] = devUserId
        config.headers['X-Dev-Org-ID'] = devOrgId
        console.log('Added development headers:', { devUserId, devOrgId })
      }
    }
    
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API response received: ${response.status}`)
    return response
  },
  (error: AxiosError) => {
    // Enhanced error logging with better error object handling
    const errorInfo = {
      message: error?.message || 'Unknown error',
      status: error?.response?.status,
      statusText: error?.response?.statusText,
      data: error?.response?.data,
      url: error?.config?.url,
      baseURL: error?.config?.baseURL,
      code: error?.code,
      name: error?.name,
      stack: error?.stack
    }
    
    console.error('API Error:', errorInfo)
    
    // Handle specific error cases
    if (error?.code === 'ECONNREFUSED' || error?.code === 'ERR_NETWORK') {
      console.error('Network Error: Backend server is not running or not accessible')
      // Trigger global error handler for network issues
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('api-error', {
          detail: { type: 'network', message: 'Unable to connect to server' }
        }))
      }
    } else if (error?.response?.status === 401) {
      console.error('Unauthorized: Token may be expired or invalid')
      // Clear token and redirect to login
      setAuthToken(null)
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('api-error', {
          detail: { type: 'unauthorized', message: 'Session expired. Please log in again.' }
        }))
      }
    } else if (error?.response?.status === 403) {
      console.error('Forbidden: Insufficient permissions')
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('api-error', {
          detail: { type: 'forbidden', message: 'You do not have permission to perform this action.' }
        }))
      }
    } else if (error?.response?.status === 404) {
      console.error('API endpoint not found:', error?.config?.url)
    } else if (error?.response?.status && error.response.status >= 500) {
      console.error('Server error:', error.response.status, error?.response?.statusText)
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('api-error', {
          detail: { type: 'server', message: 'Server error. Please try again later.' }
        }))
      }
    }
    
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: 'Admin' | 'Manager' | 'Designer'
  organization_id: string
  is_active: boolean
  created_at: string
}

export interface Organization {
  id: string
  name: string
  domain: string
  created_at: string
}

export interface UserProfile {
  id: string
  email: string
  first_name: string
  last_name: string
  role: 'Admin' | 'Manager' | 'Designer'
  organization_id: string
  organization: Organization
  is_active: boolean
  created_at: string
}

// Test API connectivity
export const testApi = {
  // Test backend connectivity
  healthCheck: async (): Promise<unknown> => {
    try {
      const response = await api.get('/health/')
      return response.data
    } catch (error: unknown) {
      console.error('Health check failed:', error)
      throw error
    }
  },
  
  // Test API status
  status: async (): Promise<unknown> => {
    try {
      const response = await api.get('/')
      return response.data
    } catch (error: unknown) {
      console.error('Status check failed:', error)
      throw error
    }
  }
}

// User Management API
export const userApi = {
  // Get current user profile
  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await api.get('/api/profiles/')
      // The API returns a list, get the first profile
      const profiles = response.data.results || response.data
      if (Array.isArray(profiles) && profiles.length > 0) {
        return profiles[0]
      }
      throw new Error('No profile found')
    } catch (error: unknown) {
      console.error('Get profile failed:', error)
      throw error
    }
  },

  // Get all users in organization (Admin only)
  getUsers: async (): Promise<User[]> => {
    const response = await api.get('/api/users/')
    return response.data
  },

  // Update user role (Admin only)
  updateUserRole: async (userId: string, role: string): Promise<User> => {
    const response = await api.patch(`/api/users/${userId}/`, { role })
    return response.data
  },

  // Remove user from organization (Admin only)
  removeUser: async (userId: string): Promise<void> => {
    await api.delete(`/api/users/${userId}/`)
  },

  // Invite user to organization (Admin only)
  inviteUser: async (email: string, role: string): Promise<void> => {
    await api.post('/api/users/invite/', { email, role })
  }
}

// Organization API
export const organizationApi = {
  // Get organization details
  getOrganization: async (): Promise<Organization> => {
    const response = await api.get('/api/organizations/current/')
    return response.data
  },

  // Update organization settings (Admin only)
  updateOrganization: async (data: Partial<Organization>): Promise<Organization> => {
    const response = await api.patch('/api/organizations/current/', data)
    return response.data
  }
}

export default api
