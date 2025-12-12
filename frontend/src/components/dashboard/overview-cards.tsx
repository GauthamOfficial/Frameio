"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, Calendar, Heart, Palette, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { apiGet } from "@/utils/api"

interface OverviewStats {
  generatedPosts: number
  scheduledPosts: number
  engagementRate: string
  brandkitCreated: number
}

export function OverviewCards() {
  const [stats, setStats] = useState<OverviewStats>({
    generatedPosts: 0,
    scheduledPosts: 0,
    engagementRate: "0%",
    brandkitCreated: 0
  })
  const [loading, setLoading] = useState(true)
  const { getToken } = useAuth()

  useEffect(() => {
    fetchStats()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      
      // Fetch generated posters count
      try {
        const postersData = await apiGet('/api/ai/ai-poster/posters/?limit=1', {}, token) as { success?: boolean; count?: number }
        if (postersData.success && postersData.count !== undefined) {
          setStats(prev => ({
            ...prev,
            generatedPosts: postersData.count || 0
          }))
        }
      } catch (postersError) {
        // Handle network errors for posters fetch gracefully
        console.warn('Failed to fetch posters count:', postersError)
        // Don't throw - continue to try other stats
      }

      // Fetch branding kits count
      try {
        const brandingKitsData = await apiGet('/api/ai/branding-kit/history/?limit=1', {}, token) as { success?: boolean; count?: number }
        if (brandingKitsData.success && brandingKitsData.count !== undefined) {
          setStats(prev => ({
            ...prev,
            brandkitCreated: brandingKitsData.count || 0
          }))
        }
      } catch (brandingKitsError) {
        // Handle network errors for branding kits fetch gracefully
        console.warn('Failed to fetch branding kits count:', brandingKitsError)
        // Don't throw - stats will remain at default values
      }

      // Fetch scheduled posts count
      try {
        // Build custom headers for organization context
        const customHeaders: Record<string, string> = {}
        if (typeof window !== 'undefined') {
          const orgSlug = window.localStorage.getItem('organizationSlug') 
            || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG 
            || null
          if (orgSlug) {
            customHeaders['X-Organization'] = orgSlug
          }
          const devOrgId = window.localStorage.getItem('devOrgId')
            || process.env.NEXT_PUBLIC_DEV_ORG_ID 
            || null
          if (devOrgId) {
            customHeaders['X-Dev-Org-Id'] = devOrgId
          }
        }

        const scheduledData = await apiGet('/api/ai/schedule/', { headers: customHeaders, credentials: 'include', mode: 'cors' }, token) as Array<{ status?: string }> | { results?: Array<{ status?: string }> }
        
        let scheduledPosts: Array<{ status?: string }> = []
        if (Array.isArray(scheduledData)) {
          scheduledPosts = scheduledData
        } else if (scheduledData.results && Array.isArray(scheduledData.results)) {
          scheduledPosts = scheduledData.results
        }

        // Filter out cancelled posts (they're "deleted" from user's perspective)
        const activePosts = scheduledPosts.filter(post => post.status !== 'cancelled')
        
        setStats(prev => ({
          ...prev,
          scheduledPosts: activePosts.length
        }))
      } catch (scheduledError) {
        // Handle network errors for scheduled posts fetch gracefully
        console.warn('Failed to fetch scheduled posts count:', scheduledError)
        // Don't throw - stats will remain at default values
      }

      // TODO: Fetch other stats when endpoints are available
      // - Engagement rate: GET /api/analytics/engagement
      
    } catch (error) {
      // This catch block handles any unexpected errors
      console.error('Error fetching stats:', error)
      // Stats will remain at default values (0)
    } finally {
      setLoading(false)
    }
  }

  const overviewData = [
    {
      title: "Generated Posters",
      value: loading ? "..." : stats.generatedPosts.toLocaleString(),
      change: "",
      trend: "up" as const,
      icon: TrendingUp,
      color: "text-chart-1"
    },
    {
      title: "Scheduled Posts",
      value: loading ? "..." : stats.scheduledPosts.toLocaleString(),
      change: "",
      trend: "up" as const,
      icon: Calendar,
      color: "text-chart-2"
    },
    {
      title: "Engagement Rate",
      value: loading ? "..." : stats.engagementRate,
      change: "",
      trend: "up" as const,
      icon: Heart,
      color: "text-chart-3"
    },
    {
      title: "Brandkit Created",
      value: loading ? "..." : stats.brandkitCreated.toLocaleString(),
      change: "",
      trend: "up" as const,
      icon: Palette,
      color: "text-chart-4"
    }
  ]

  return (
    <div className="grid grid-cols-1 min-[475px]:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-6 sm:mb-8">
      {overviewData.map((item) => {
        const Icon = item.icon
        return (
          <Card key={item.title} className="textile-hover textile-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 p-4 sm:p-6">
              <CardTitle className="text-xs sm:text-sm font-medium text-muted-foreground truncate pr-2">
                {item.title}
              </CardTitle>
              {loading ? (
                <Loader2 className={`h-3 w-3 sm:h-4 sm:w-4 ${item.color} animate-spin shrink-0`} />
              ) : (
                <Icon className={`h-3 w-3 sm:h-4 sm:w-4 ${item.color} shrink-0`} />
              )}
            </CardHeader>
            <CardContent className="p-4 sm:p-6 pt-0">
              <div className="text-xl sm:text-2xl font-bold text-foreground">{item.value}</div>
              {item.change && (
                <p className="text-xs text-muted-foreground mt-1">
                  <span className="text-green-600">{item.change}</span> from last month
                </p>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

