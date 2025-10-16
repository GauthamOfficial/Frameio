/**
 * Company Profile Hook
 * Custom hook for managing company profile data in components
 */

import { useState, useEffect } from 'react'
import { useAuth } from '@clerk/nextjs'
import { companyProfileService, CompanyProfile, ProfileStatus } from '@/lib/company-profile-service'

export interface UseCompanyProfileReturn {
  profile: CompanyProfile | null
  status: ProfileStatus | null
  loading: boolean
  error: string | null
  hasBrandingData: boolean
  brandingData: any
  contactInfoText: string
  refreshProfile: () => Promise<void>
}

export function useCompanyProfile(): UseCompanyProfileReturn {
  const { getToken } = useAuth()
  const [profile, setProfile] = useState<CompanyProfile | null>(null)
  const [status, setStatus] = useState<ProfileStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProfile = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get auth token
      const token = await getToken()
      companyProfileService.setAuthToken(token)

      // Fetch profile and status in parallel
      const [profileData, statusData] = await Promise.all([
        companyProfileService.getCompanyProfile(),
        companyProfileService.getProfileStatus()
      ])

      setProfile(profileData)
      setStatus(statusData)

      console.log('✅ Company profile loaded:', {
        hasProfile: !!profileData,
        hasBranding: companyProfileService.hasBrandingData(profileData),
        completion: statusData?.completion_percentage || 0
      })

    } catch (err) {
      console.error('❌ Error loading company profile:', err)
      setError(err instanceof Error ? err.message : 'Failed to load company profile')
    } finally {
      setLoading(false)
    }
  }

  const refreshProfile = async () => {
    await loadProfile()
  }

  useEffect(() => {
    loadProfile()
  }, [])

  const hasBrandingData = companyProfileService.hasBrandingData(profile)
  const brandingData = companyProfileService.getBrandingData(profile)
  const contactInfoText = companyProfileService.formatContactInfo(profile)

  return {
    profile,
    status,
    loading,
    error,
    hasBrandingData,
    brandingData,
    contactInfoText,
    refreshProfile
  }
}
