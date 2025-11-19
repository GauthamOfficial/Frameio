"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, Calendar, Heart, Palette, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"

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
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      
      // Fetch generated posters count
      const postersResponse = await fetch(`${apiBase}/api/ai/ai-poster/posters/?limit=1`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (postersResponse.ok) {
        const postersData = await postersResponse.json()
        if (postersData.success) {
          setStats(prev => ({
            ...prev,
            generatedPosts: postersData.count || 0
          }))
        }
      }

      // Fetch branding kits count
      const brandingKitsResponse = await fetch(`${apiBase}/api/ai/branding-kit/history/?limit=1`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include'
      })

      if (brandingKitsResponse.ok) {
        const brandingKitsData = await brandingKitsResponse.json()
        if (brandingKitsData.success) {
          setStats(prev => ({
            ...prev,
            brandkitCreated: brandingKitsData.count || 0
          }))
        }
      }

      // TODO: Fetch other stats when endpoints are available
      // - Scheduled posts: GET /api/scheduler/posts/count
      // - Engagement rate: GET /api/analytics/engagement
      
    } catch (error) {
      console.error('Error fetching stats:', error)
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {overviewData.map((item) => {
        const Icon = item.icon
        return (
          <Card key={item.title} className="textile-hover textile-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {item.title}
              </CardTitle>
              {loading ? (
                <Loader2 className={`h-4 w-4 ${item.color} animate-spin`} />
              ) : (
                <Icon className={`h-4 w-4 ${item.color}`} />
              )}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{item.value}</div>
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

