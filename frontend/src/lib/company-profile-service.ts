/**
 * Company Profile Service
 * Handles fetching and managing company profile data for poster generation
 */

import { API_ENDPOINTS, API_BASE_URL } from './config'

export interface CompanyProfile {
  id?: string
  company_name?: string
  logo?: string
  logo_url?: string
  whatsapp_number?: string
  email?: string
  facebook_link?: string
  website?: string
  address?: string
  description?: string
  brand_colors?: string[]
  preferred_logo_position?: string
  has_complete_profile?: boolean
  contact_info?: {
    whatsapp?: string
    email?: string
    facebook?: string
  }
  created_at?: string
  updated_at?: string
}

export interface ProfileStatus {
  has_profile: boolean
  has_logo: boolean
  has_contact_info: boolean
  completion_percentage: number
}

class CompanyProfileService {
  private authToken: string | null = null

  setAuthToken(token: string | null) {
    this.authToken = token
  }

  private getAuthHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`
    }

    // Multitenancy headers
    try {
      const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null)
        || (process.env.NEXT_PUBLIC_ORGANIZATION_SLUG as string | undefined)
      if (orgSlug) headers['X-Organization'] = orgSlug

      const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
        || (process.env.NEXT_PUBLIC_DEV_ORG_ID as string | undefined)
      if (devOrgId) headers['X-Dev-Org-Id'] = devOrgId
    } catch {}

    return headers
  }

  /**
   * Fetch company profile data
   */
  async getCompanyProfile(): Promise<CompanyProfile | null> {
    try {
      console.log('🔍 Fetching company profile...')
      console.log('API Endpoint:', API_ENDPOINTS.COMPANY_PROFILES)
      console.log('Auth Headers:', this.getAuthHeaders())
      
      const response = await fetch(API_ENDPOINTS.COMPANY_PROFILES, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      console.log('Company profile response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const profile = await response.json()
        console.log('✅ Company profile fetched:', profile)
        return profile
      } else {
        const errorText = await response.text()
        console.log('❌ Failed to fetch company profile:', response.status, errorText)
        return null
      }
    } catch (error) {
      console.error('❌ Error fetching company profile:', error)
      
      // Check if it's a network error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.warn('⚠️ Network error - backend server may not be running')
        console.warn(`⚠️ Attempted to fetch from: ${API_ENDPOINTS.COMPANY_PROFILES}`)
        console.warn('💡 Make sure the backend server is running: cd backend && python manage.py runserver')
        console.warn('💡 Check if CORS is properly configured in backend settings')
      } else if (error instanceof Error) {
        console.error('Error details:', error.message)
      }
      
      return null
    }
  }

  /**
   * Get profile completion status
   */
  async getProfileStatus(): Promise<ProfileStatus | null> {
    try {
      console.log('🔍 Fetching profile status...')
      console.log('API Endpoint:', API_ENDPOINTS.COMPANY_PROFILES_STATUS)
      console.log('Auth Headers:', this.getAuthHeaders())
      
      const response = await fetch(API_ENDPOINTS.COMPANY_PROFILES_STATUS, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      console.log('Profile status response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const status = await response.json()
        console.log('✅ Profile status fetched:', status)
        return status
      } else {
        const errorText = await response.text()
        console.log('❌ Failed to fetch profile status:', response.status, errorText)
        return null
      }
    } catch (error) {
      console.error('❌ Error fetching profile status:', error)
      
      // Check if it's a network error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.warn('⚠️ Network error - backend server may not be running')
        console.warn(`⚠️ Attempted to fetch from: ${API_ENDPOINTS.COMPANY_PROFILES_STATUS}`)
        console.warn('💡 Make sure the backend server is running: cd backend && python manage.py runserver')
        console.warn('💡 Check if CORS is properly configured in backend settings')
      } else if (error instanceof Error) {
        console.error('Error details:', error.message)
      }
      
      return null
    }
  }

  /**
   * Check if company profile has branding data
   */
  hasBrandingData(profile: CompanyProfile | null): boolean {
    if (!profile) return false
    
    const hasLogo = !!(profile.logo || profile.logo_url)
    const hasContactInfo = !!(profile.whatsapp_number || profile.email || profile.facebook_link)
    const hasCompanyName = !!profile.company_name
    
    return hasLogo || hasContactInfo || hasCompanyName
  }

  /**
   * Get branding data for poster generation
   */
  getBrandingData(profile: CompanyProfile | null) {
    if (!profile || !this.hasBrandingData(profile)) {
      return null
    }

    return {
      company_name: profile.company_name,
      logo_url: profile.logo_url || (profile.logo ? `${API_BASE_URL}${profile.logo}` : null),
      contact_info: {
        whatsapp: profile.whatsapp_number,
        email: profile.email,
        facebook: profile.facebook_link
      },
      brand_colors: profile.brand_colors || [],
      preferred_logo_position: profile.preferred_logo_position || 'top_right'
    }
  }

  /**
   * Format contact information for display
   */
  formatContactInfo(profile: CompanyProfile | null): string {
    if (!profile) return ''

    let contactText = ''
    
    if (profile.whatsapp_number) {
      contactText += `📱 WhatsApp: ${profile.whatsapp_number}\n`
    }
    
    if (profile.email) {
      contactText += `✉️ Email: ${profile.email}\n`
    }
    
    return contactText.trim()
  }
}

// Export singleton instance
export const companyProfileService = new CompanyProfileService()
export default companyProfileService
