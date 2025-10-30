'use client';

import { useState } from 'react';
import { useAdminAuth } from '@/contexts/admin-auth-context';
import { StatsCard } from '@/components/admin/StatsCard';
import { AnalyticsChart } from '@/components/admin/AnalyticsChart';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Users, 
  Image, 
  TrendingUp, 
  Building2,
  Activity,
  Clock,
  Shield,
  Loader2,
  AlertCircle
} from 'lucide-react';

function AdminLoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAdminAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(username, password);
      
      if (!result.success) {
        setError(result.error || 'Invalid credentials');
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-primary/10 rounded-full">
              <Shield className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Admin Dashboard</CardTitle>
          <CardDescription>
            Enter your credentials to access the admin panel
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>Protected admin area</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function AdminDashboard() {
  // Mock data - Replace with real data from your API
  const stats = {
    totalUsers: 1247,
    totalPosts: 8934,
    activeCompanies: 156,
    averageEngagement: '8.2%',
  };

  const aspectRatioData = [
    { label: '1:1 Square', value: 450 },
    { label: '16:9 Landscape', value: 320 },
    { label: '9:16 Portrait', value: 280 },
    { label: '4:5 Instagram', value: 210 },
    { label: '2:3 Pinterest', value: 150 },
  ];

  const topCompanies = [
    { label: 'Fashion Textiles Co.', value: 234 },
    { label: 'Modern Fabrics Ltd.', value: 198 },
    { label: 'Elite Designs Inc.', value: 176 },
    { label: 'Textile Masters', value: 145 },
    { label: 'Fabric Innovations', value: 132 },
  ];

  const recentActivity = [
    { user: 'John Doe', action: 'Generated AI poster', time: '2 minutes ago' },
    { user: 'Jane Smith', action: 'Created new branding kit', time: '15 minutes ago' },
    { user: 'Mike Johnson', action: 'Updated company profile', time: '1 hour ago' },
    { user: 'Sarah Williams', action: 'Downloaded 5 designs', time: '2 hours ago' },
    { user: 'Tom Brown', action: 'Invited team member', time: '3 hours ago' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
        <p className="text-muted-foreground">
          Monitor platform metrics and user activity
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={stats.totalUsers.toLocaleString()}
          description="+12% from last month"
          icon={Users}
          trend={{ value: '12%', isPositive: true }}
        />
        <StatsCard
          title="AI Posts Generated"
          value={stats.totalPosts.toLocaleString()}
          description="+23% from last month"
          icon={Image}
          trend={{ value: '23%', isPositive: true }}
        />
        <StatsCard
          title="Active Companies"
          value={stats.activeCompanies}
          description="+8 new this month"
          icon={Building2}
          trend={{ value: '5.4%', isPositive: true }}
        />
        <StatsCard
          title="Avg. Engagement"
          value={stats.averageEngagement}
          description="+2.1% from last week"
          icon={TrendingUp}
          trend={{ value: '2.1%', isPositive: true }}
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 md:grid-cols-2">
        <AnalyticsChart
          title="Most Used Aspect Ratios"
          description="Popular poster dimensions"
          data={aspectRatioData}
        />
        <AnalyticsChart
          title="Most Active Textile Companies"
          description="By posts generated"
          data={topCompanies}
        />
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest user actions on the platform</CardDescription>
            </div>
            <Activity className="h-5 w-5 text-muted-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                    {activity.user.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{activity.user}</p>
                    <p className="text-sm text-muted-foreground">{activity.action}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  {activity.time}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function AdminDashboardPage() {
  const { isAuthenticated } = useAdminAuth();

  // Show login form if not authenticated, otherwise show dashboard
  if (!isAuthenticated) {
    return <AdminLoginForm />;
  }

  return <AdminDashboard />;
}
