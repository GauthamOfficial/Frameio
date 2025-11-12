'use client';

import { useState, useEffect } from 'react';
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
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPosts: 0,
    activeCompanies: 0,
    averageEngagement: '0%',
  });

  // Load real data on mount
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch real user count
      const usersResponse = await fetch('/api/admin/users', {
        credentials: 'include',
      });
      
      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        const userCount = usersData.count || (Array.isArray(usersData) ? usersData.length : 0);
        
        setStats(prev => ({
          ...prev,
          totalUsers: userCount,
        }));
      }
      
      // TODO: Add more API calls for other stats when endpoints are available
      // - Total posts: GET /api/admin/posts or similar
      // - Active companies: GET /api/admin/companies or similar
      // - Average engagement: GET /api/admin/analytics or similar
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const aspectRatioData: { label: string; value: number }[] = [];
  const topCompanies: { label: string; value: number }[] = [];
  const recentActivity: { user: string; action: string; time: string }[] = [];

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
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Total Users"
            value={stats.totalUsers.toLocaleString()}
            description="From database"
            icon={Users}
          />
          <StatsCard
            title="AI Posts Generated"
            value={stats.totalPosts.toLocaleString()}
            description="Data not available"
            icon={Image}
          />
          <StatsCard
            title="Active Companies"
            value={stats.activeCompanies}
            description="Data not available"
            icon={Building2}
          />
          <StatsCard
            title="Avg. Engagement"
            value={stats.averageEngagement}
            description="Data not available"
            icon={TrendingUp}
          />
        </div>
      )}

      {/* Charts Row */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Most Used Aspect Ratios</CardTitle>
            <CardDescription>Popular poster dimensions</CardDescription>
          </CardHeader>
          <CardContent>
            {aspectRatioData.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <Activity className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>No analytics data available</p>
                  <p className="text-sm mt-1">Data will appear once posts are generated</p>
                </div>
              </div>
            ) : (
              <AnalyticsChart
                title="Most Used Aspect Ratios"
                description="Popular poster dimensions"
                data={aspectRatioData}
              />
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Most Active Textile Companies</CardTitle>
            <CardDescription>By posts generated</CardDescription>
          </CardHeader>
          <CardContent>
            {topCompanies.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <Building2 className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>No company data available</p>
                  <p className="text-sm mt-1">Data will appear once companies are active</p>
                </div>
              </div>
            ) : (
              <AnalyticsChart
                title="Most Active Textile Companies"
                description="By posts generated"
                data={topCompanies}
              />
            )}
          </CardContent>
        </Card>
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
          {recentActivity.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-gray-400">
              <div className="text-center">
                <Clock className="h-12 w-12 mx-auto mb-2 opacity-20" />
                <p>No recent activity</p>
                <p className="text-sm mt-1">User activity will be displayed here</p>
              </div>
            </div>
          ) : (
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
          )}
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
