'use client';

import { useState, useEffect } from 'react';
import { StatsCard } from '@/components/admin/StatsCard';
import { AnalyticsChart } from '@/components/admin/AnalyticsChart';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Users, 
  Download,
  Calendar,
  Eye,
  BarChart3,
  AlertCircle
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface AnalyticsData {
  overview: {
    totalUsers: number;
    totalSessions: number;
    pageViews: number;
    avgSessionDuration: string;
    bounceRate: string;
    trends?: {
      users: string;
      sessions: string;
      views: string;
    };
    error?: string;
  };
  userGrowth: Array<{ label: string; value: number }>;
  deviceBreakdown: Array<{ label: string; value: number }>;
  topPages: Array<{ path: string; views: number; title: string }>;
  trafficSources: Array<{ source: string; sessions: number }>;
}

export default function AdminAnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [configured, setConfigured] = useState<boolean>(false);

  useEffect(() => {
    loadAnalyticsData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/admin/analytics?timeRange=${timeRange}`, {
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // Authentication error - redirect to login or show message
          setError(data.error || 'Authentication required. Please log in to the admin panel.');
          setAnalyticsData(null);
          setConfigured(false);
          return;
        }
        if (response.status === 503) {
          // Service not configured
          setConfigured(false);
          setError(data.message || 'Google Analytics is not configured');
          setAnalyticsData(null);
          return;
        }
        throw new Error(data.error || 'Failed to fetch analytics data');
      }

      if (!data.configured) {
        setConfigured(false);
        setError(data.message || 'Google Analytics is not configured');
        setAnalyticsData(null);
        return;
      }

      setConfigured(true);
      setAnalyticsData(data.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
      setAnalyticsData(null);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const parseTrend = (trendStr?: string): { value: string; isPositive: boolean } => {
    if (!trendStr) return { value: '0%', isPositive: true };
    const match = trendStr.match(/^([+-]?[\d.]+)%$/);
    if (!match) return { value: '0%', isPositive: true };
    const value = parseFloat(match[1]);
    return {
      value: trendStr,
      isPositive: value >= 0
    };
  };

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground">
              Platform performance and user insights
            </p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 animate-pulse text-muted-foreground" />
            <p className="text-muted-foreground">Loading analytics data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error/not configured state
  if (!configured || !analyticsData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground">
              Platform performance and user insights
            </p>
          </div>
        </div>

        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Google Analytics Not Configured</AlertTitle>
          <AlertDescription>
            {error || 'Google Analytics is not configured. Please set up GOOGLE_ANALYTICS_PROPERTY_ID and credentials in your backend environment variables.'}
            <br />
            <br />
            <strong>Required environment variables:</strong>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>GOOGLE_ANALYTICS_PROPERTY_ID - Your GA4 Property ID</li>
              <li>GOOGLE_ANALYTICS_CREDENTIALS_JSON - Service account credentials as JSON string</li>
              <li>Or GOOGLE_ANALYTICS_CREDENTIALS_PATH - Path to service account credentials file</li>
            </ul>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const { overview, userGrowth, deviceBreakdown, topPages, trafficSources } = analyticsData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Real-time platform performance and user insights from Google Analytics
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              const ranges: Array<'7d' | '30d' | '90d' | '1y'> = ['7d', '30d', '90d', '1y'];
              const currentIndex = ranges.indexOf(timeRange);
              const nextIndex = (currentIndex + 1) % ranges.length;
              setTimeRange(ranges[nextIndex]);
            }}
          >
            <Calendar className="mr-2 h-4 w-4" />
            {timeRange === '7d' && 'Last 7 days'}
            {timeRange === '30d' && 'Last 30 days'}
            {timeRange === '90d' && 'Last 90 days'}
            {timeRange === '1y' && 'Last year'}
          </Button>
          <Button variant="outline" size="sm" onClick={loadAnalyticsData}>
            <Download className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={formatNumber(overview.totalUsers)}
          description="Active users"
          icon={Users}
          trend={parseTrend(overview.trends?.users)}
        />
        <StatsCard
          title="Page Views"
          value={formatNumber(overview.pageViews)}
          description="Total page views"
          icon={Eye}
          trend={parseTrend(overview.trends?.views)}
        />
        <StatsCard
          title="Sessions"
          value={formatNumber(overview.totalSessions)}
          description="Total sessions"
          icon={BarChart3}
          trend={parseTrend(overview.trends?.sessions)}
        />
        <StatsCard
          title="Avg. Session Time"
          value={overview.avgSessionDuration}
          description="Per user session"
          icon={TrendingUp}
          trend={{ value: '—', isPositive: true }}
        />
      </div>

      {/* Growth Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <AnalyticsChart
          title="User Growth"
          description="Active users over time"
          data={userGrowth}
        />
        <AnalyticsChart
          title="Device Breakdown"
          description="User device distribution (%)"
          data={deviceBreakdown}
        />
      </div>

      {/* Top Pages & Traffic Sources */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Top Pages */}
        <Card>
          <CardHeader>
            <CardTitle>Top Pages</CardTitle>
            <CardDescription>Most viewed pages</CardDescription>
          </CardHeader>
          <CardContent>
            {topPages.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>No page data available</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {topPages.map((page, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                  >
                    <div className="space-y-1 flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{page.title}</p>
                      <p className="text-xs text-muted-foreground truncate">{page.path}</p>
                    </div>
                    <Badge variant="secondary" className="ml-4">
                      {formatNumber(page.views)} views
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Traffic Sources */}
        <Card>
          <CardHeader>
            <CardTitle>Traffic Sources</CardTitle>
            <CardDescription>Where your visitors come from</CardDescription>
          </CardHeader>
          <CardContent>
            {trafficSources.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>No traffic source data available</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {trafficSources.map((source, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{source.source || 'direct'}</p>
                    </div>
                    <Badge variant="secondary" className="ml-4">
                      {formatNumber(source.sessions)} sessions
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
