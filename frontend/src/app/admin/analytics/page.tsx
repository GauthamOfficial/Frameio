'use client';

import { useState } from 'react';
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
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  // Mock analytics data
  const overviewStats = {
    totalRevenue: '$12,450',
    totalViews: 45678,
    conversionRate: '3.2%',
    avgSessionTime: '4m 32s',
  };

  const userGrowthData = [
    { label: 'Jan', value: 120 },
    { label: 'Feb', value: 150 },
    { label: 'Mar', value: 180 },
    { label: 'Apr', value: 220 },
    { label: 'May', value: 280 },
    { label: 'Jun', value: 340 },
  ];

  const postGenerationData = [
    { label: 'Jan', value: 450 },
    { label: 'Feb', value: 680 },
    { label: 'Mar', value: 820 },
    { label: 'Apr', value: 950 },
    { label: 'May', value: 1200 },
    { label: 'Jun', value: 1450 },
  ];

  const topFeatures = [
    { name: 'AI Poster Generator', usage: 2340, growth: '+23%' },
    { name: 'Branding Kit', usage: 1890, growth: '+18%' },
    { name: 'Template Library', usage: 1456, growth: '+12%' },
    { name: 'Collaboration Tools', usage: 987, growth: '+8%' },
    { name: 'Export & Download', usage: 756, growth: '+15%' },
  ];

  const deviceBreakdown = [
    { label: 'Desktop', value: 65 },
    { label: 'Mobile', value: 25 },
    { label: 'Tablet', value: 10 },
  ];

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

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Total Revenue"
          value={overviewStats.totalRevenue}
          description="This month"
          icon={DollarSign}
          trend={{ value: '12.5%', isPositive: true }}
        />
        <StatsCard
          title="Total Views"
          value={overviewStats.totalViews.toLocaleString()}
          description="Page views this month"
          icon={Eye}
          trend={{ value: '8.2%', isPositive: true }}
        />
        <StatsCard
          title="Conversion Rate"
          value={overviewStats.conversionRate}
          description="Trial to paid"
          icon={TrendingUp}
          trend={{ value: '0.5%', isPositive: true }}
        />
        <StatsCard
          title="Avg. Session Time"
          value={overviewStats.avgSessionTime}
          description="Per user session"
          icon={Users}
          trend={{ value: '12s', isPositive: true }}
        />
      </div>

      {/* Growth Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <AnalyticsChart
          title="User Growth"
          description="New users per month"
          data={userGrowthData}
        />
        <AnalyticsChart
          title="Post Generation"
          description="AI posts created per month"
          data={postGenerationData}
        />
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
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    {feature.growth}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Device Breakdown */}
        <AnalyticsChart
          title="Device Breakdown"
          description="User device distribution (%)"
          data={deviceBreakdown}
        />
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
        </CardContent>
      </Card>
    </div>
  );
}

