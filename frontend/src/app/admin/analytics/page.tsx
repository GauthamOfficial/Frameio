'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { API_BASE_URL } from '@/lib/config';
import { StatsCard } from '@/components/admin/StatsCard';
import { AnalyticsChart } from '@/components/admin/AnalyticsChart';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Users, 
  Image, 
  Download,
  Calendar,
  DollarSign,
  Eye,
  BarChart3
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function AdminAnalyticsPage() {
  const { getToken } = useAuth();
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalRevenue, setTotalRevenue] = useState<string>('');
  const [totalViews, setTotalViews] = useState<number>(0);
  const [conversionRate, setConversionRate] = useState<string>('');
  const [avgSessionTime, setAvgSessionTime] = useState<string>('');
  const [userGrowthData, setUserGrowthData] = useState<{ label: string; value: number }[]>([]);
  const [postGenerationData, setPostGenerationData] = useState<{ label: string; value: number }[]>([]);
  const [topFeatures, setTopFeatures] = useState<{ name: string; usage: number; growth?: string }[]>([]);
  const [deviceBreakdown, setDeviceBreakdown] = useState<{ label: string; value: number }[]>([]);

  useEffect(() => {
    let isMounted = true;
    async function loadAnalytics() {
      try {
        setIsLoading(true);
        setError(null);
        const token = (await getToken()) || 'test_clerk_token';
        const devHeaders = process.env.NODE_ENV !== 'production'
          ? { 
              'X-Dev-User-Id': '684af5c8-5dd6-4c20-911c-3c8c39a5ca86', 
              'X-Dev-Org-Id': '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb' 
            }
          : {};
        const res = await fetch(`${API_BASE_URL}/api/ai/analytics/`, { 
          cache: 'no-store', 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...devHeaders
          } 
        });
        if (res.ok) {
          const data = await res.json();
          if (!isMounted) return;
          // Best-effort mapping
          if (data) {
            if (data.total_revenue || data.revenue) setTotalRevenue(String(data.total_revenue ?? data.revenue));
            if (data.total_views || data.views) setTotalViews(Number(data.total_views ?? data.views ?? 0));
            if (data.conversion_rate || data.conversion) setConversionRate(String(data.conversion_rate ?? data.conversion));
            if (data.avg_session_time || data.average_session) setAvgSessionTime(String(data.avg_session_time ?? data.average_session));

            if (Array.isArray(data.user_growth)) {
              setUserGrowthData(
                data.user_growth
                  .filter((d: any) => d && (d.label || d.month) && (d.value ?? d.count) !== undefined)
                  .map((d: any) => ({ label: d.label ?? d.month, value: d.value ?? d.count }))
              );
            }
            if (Array.isArray(data.post_generation)) {
              setPostGenerationData(
                data.post_generation
                  .filter((d: any) => d && (d.label || d.month) && (d.value ?? d.count) !== undefined)
                  .map((d: any) => ({ label: d.label ?? d.month, value: d.value ?? d.count }))
              );
            }
            if (Array.isArray(data.top_features)) {
              setTopFeatures(
                data.top_features
                  .filter((f: any) => f && (f.name || f.feature))
                  .map((f: any) => ({ name: f.name ?? f.feature, usage: f.usage ?? f.count ?? 0, growth: f.growth }))
              );
            }
            if (Array.isArray(data.device_breakdown)) {
              setDeviceBreakdown(
                data.device_breakdown
                  .filter((d: any) => d && d.label && (d.value ?? d.percent) !== undefined)
                  .map((d: any) => ({ label: d.label, value: d.value ?? d.percent }))
              );
            }
          }
        }
      } catch (e: any) {
        if (isMounted) setError(e?.message || 'Failed to load analytics');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadAnalytics();
    return () => { isMounted = false; };
  }, [timeRange]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Platform performance and user insights
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Calendar className="mr-2 h-4 w-4" />
            {timeRange === '7d' && 'Last 7 days'}
            {timeRange === '30d' && 'Last 30 days'}
            {timeRange === '90d' && 'Last 90 days'}
            {timeRange === '1y' && 'Last year'}
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Overview Stats (show only available values) */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Total Revenue"
          value={totalRevenue || '-'}
          description=""
          icon={DollarSign}
          trend={undefined}
        />
        <StatsCard
          title="Total Views"
          value={totalViews ? totalViews.toLocaleString() : '-'}
          description=""
          icon={Eye}
          trend={undefined}
        />
        <StatsCard
          title="Conversion Rate"
          value={conversionRate || '-'}
          description=""
          icon={TrendingUp}
          trend={undefined}
        />
        <StatsCard
          title="Avg. Session Time"
          value={avgSessionTime || '-'}
          description=""
          icon={Users}
          trend={undefined}
        />
      </div>

      {/* Growth Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {userGrowthData.length > 0 && (
          <AnalyticsChart
            title="User Growth"
            description="New users per month"
            data={userGrowthData}
          />
        )}
        {postGenerationData.length > 0 && (
          <AnalyticsChart
            title="Post Generation"
            description="AI posts created per month"
            data={postGenerationData}
          />
        )}
      </div>

      {/* Feature Usage & Device Breakdown */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Top Features */}
        <Card>
          <CardHeader>
            <CardTitle>Top Features</CardTitle>
            <CardDescription>Most used platform features</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topFeatures.map((feature, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{feature.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {feature.usage.toLocaleString()} uses
                    </p>
                  </div>
                  {feature.growth && (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {feature.growth}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Device Breakdown */}
        {deviceBreakdown.length > 0 && (
          <AnalyticsChart
            title="Device Breakdown"
            description="User device distribution (%)"
            data={deviceBreakdown}
          />
        )}
      </div>

      {/* Google Analytics Integration Placeholder */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle>Google Analytics Integration</CardTitle>
          <CardDescription>
            Connect your Google Analytics account for advanced insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="mb-4 rounded-full bg-muted p-3">
              <BarChart3 className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">Coming Soon</h3>
            <p className="mb-4 max-w-md text-sm text-muted-foreground">
              Google Analytics integration is currently in development. 
              Connect your GA4 property to get deeper insights into user behavior and traffic sources.
            </p>
            <Button disabled>
              Connect Google Analytics
            </Button>
          </div>
          {error && (
            <div className="mt-4 text-sm text-red-600">{error}</div>
          )}
          {isLoading && (
            <div className="mt-2 text-sm text-muted-foreground">Loading analytics...</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

