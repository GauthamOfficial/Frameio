'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { API_BASE_URL } from '@/lib/config';
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
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalUsers, setTotalUsers] = useState<number>(0);
  const [totalPosts, setTotalPosts] = useState<number>(0);
  const [activeCompanies, setActiveCompanies] = useState<number>(0);
  const [averageEngagement, setAverageEngagement] = useState<string>('0%');
  const [aspectRatioData, setAspectRatioData] = useState<{ label: string; value: number }[]>([]);
  const [topCompanies, setTopCompanies] = useState<{ label: string; value: number }[]>([]);
  const [recentActivity, setRecentActivity] = useState<{ user: string; action: string; time: string }[]>([]);

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);
        const token = (await getToken()) || 'test_clerk_token';
        const authHeaders = { Authorization: `Bearer ${token}` };

        // Fetch users
        const devHeaders = process.env.NODE_ENV !== 'production'
          ? { 
              'X-Dev-User-Id': '684af5c8-5dd6-4c20-911c-3c8c39a5ca86', 
              'X-Dev-Org-Id': '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb' 
            }
          : {};
        const usersRes = await fetch(`${API_BASE_URL}/api/users/`, { cache: 'no-store', headers: { ...authHeaders, 'Content-Type': 'application/json', ...devHeaders } });
        if (usersRes.ok) {
          const usersData = await usersRes.json();
          if (isMounted) {
            const usersArray = Array.isArray(usersData) ? usersData : usersData?.results || [];
            setTotalUsers(usersArray.length);
          }
        }

        // Fetch organizations (to compute active companies if available)
        const orgRes = await fetch(`${API_BASE_URL}/api/organizations/`, { cache: 'no-store', headers: { ...authHeaders, 'Content-Type': 'application/json', ...devHeaders } });
        if (orgRes.ok) {
          const orgData = await orgRes.json();
          if (isMounted) {
            const orgArray = Array.isArray(orgData) ? orgData : orgData?.results || [];
            setActiveCompanies(orgArray.length);
          }
        }

        // Fetch analytics if available
        const analyticsRes = await fetch(`${API_BASE_URL}/api/ai/analytics/`, { cache: 'no-store', headers: { ...authHeaders, 'Content-Type': 'application/json', ...devHeaders } });
        if (analyticsRes.ok) {
          const analyticsData = await analyticsRes.json();
          if (isMounted && analyticsData) {
            // Best-effort mapping without assuming exact schema
            const posts = analyticsData.total_posts || analyticsData.post_count || 0;
            const engagement = analyticsData.average_engagement || analyticsData.avg_engagement || 0;
            const ratios = analyticsData.aspect_ratios || [];
            const companies = analyticsData.top_companies || [];
            const activity = analyticsData.recent_activity || [];

            setTotalPosts(typeof posts === 'number' ? posts : Number(posts) || 0);
            setAverageEngagement(
              typeof engagement === 'string'
                ? engagement
                : `${Number(engagement || 0).toFixed(1)}%`
            );
            if (Array.isArray(ratios)) {
              setAspectRatioData(
                ratios
                  .filter((r: any) => r && r.label && (r.value ?? r.count) !== undefined)
                  .map((r: any) => ({ label: r.label, value: r.value ?? r.count }))
              );
            }
            if (Array.isArray(companies)) {
              setTopCompanies(
                companies
                  .filter((c: any) => c && (c.name || c.label))
                  .map((c: any) => ({ label: c.label ?? c.name, value: c.value ?? c.count ?? 0 }))
              );
            }
            if (Array.isArray(activity)) {
              setRecentActivity(
                activity
                  .filter((a: any) => a && (a.user || a.username) && (a.action || a.event))
                  .map((a: any) => ({
                    user: a.user ?? a.username,
                    action: a.action ?? a.event,
                    time: a.time_ago ?? a.time ?? ''
                  }))
              );
            }
          }
        }
      } catch (e) {
        if (isMounted) setError('Failed to load dashboard data');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadData();
    return () => {
      isMounted = false;
    };
  }, []);

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
          value={totalUsers.toLocaleString()}
          description=""
          icon={Users}
          trend={undefined}
        />
        <StatsCard
          title="AI Posts Generated"
          value={totalPosts.toLocaleString()}
          description=""
          icon={Image}
          trend={undefined}
        />
        <StatsCard
          title="Active Companies"
          value={activeCompanies}
          description=""
          icon={Building2}
          trend={undefined}
        />
        <StatsCard
          title="Avg. Engagement"
          value={averageEngagement}
          description=""
          icon={TrendingUp}
          trend={undefined}
        />
      </div>

      {/* Charts Row (render only if data is present) */}
      {(aspectRatioData.length > 0 || topCompanies.length > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          {aspectRatioData.length > 0 && (
            <AnalyticsChart
              title="Most Used Aspect Ratios"
              description="Popular poster dimensions"
              data={aspectRatioData}
            />
          )}
          {topCompanies.length > 0 && (
            <AnalyticsChart
              title="Most Active Textile Companies"
              description="By posts generated"
              data={topCompanies}
            />
          )}
        </div>
      )}

      {/* Recent Activity */}
      {recentActivity.length > 0 && (
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
      )}
      {error && (
        <div className="text-sm text-red-600">{error}</div>
      )}
      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading data...
        </div>
      )}
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
