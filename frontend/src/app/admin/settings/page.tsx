'use client';

import { useState } from 'react';
import { useAdminAuth } from '@/contexts/admin-auth-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { 
  User, 
  Lock, 
  Bell, 
  Shield,
  Moon,
  Sun,
  Save,
  Loader2
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function AdminSettingsPage() {
  const { username, logout } = useAdminAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [newUserAlerts, setNewUserAlerts] = useState(true);
  const [systemAlerts, setSystemAlerts] = useState(true);
  const [weeklyReports, setWeeklyReports] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsLoading(false);
    alert('Password changed successfully');
    
    // Clear form
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handleSaveSettings = async () => {
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsLoading(false);
    alert('Settings saved successfully');
  };

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your admin account and preferences
        </p>
      </div>

      {/* Admin Profile */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <User className="h-5 w-5" />
            <div>
              <CardTitle>Admin Profile</CardTitle>
              <CardDescription>Your admin account information</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-2xl font-bold text-white">
              {username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-semibold">{username}</p>
              <Badge variant="secondary" className="mt-1">
                <Shield className="mr-1 h-3 w-3" />
                Administrator
              </Badge>
            </div>
          </div>
          
          <Separator />
          
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Username</Label>
              <Input value={username || ''} disabled className="mt-1.5" />
            </div>
            <div>
              <Label>Role</Label>
              <Input value="Super Administrator" disabled className="mt-1.5" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Lock className="h-5 w-5" />
            <div>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>Update your admin password</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="mt-1.5"
              />
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Changing Password...
                </>
              ) : (
                <>
                  <Lock className="mr-2 h-4 w-4" />
                  Change Password
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {isDarkMode ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            <div>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>Customize your dashboard appearance</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Dark Mode</Label>
              <p className="text-sm text-muted-foreground">
                Switch between light and dark themes
              </p>
            </div>
            <Switch checked={isDarkMode} onCheckedChange={toggleTheme} />
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Bell className="h-5 w-5" />
            <div>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>Manage your notification preferences</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive notifications via email
              </p>
            </div>
            <Switch 
              checked={emailNotifications} 
              onCheckedChange={setEmailNotifications} 
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>New User Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Get notified when new users sign up
              </p>
            </div>
            <Switch 
              checked={newUserAlerts} 
              onCheckedChange={setNewUserAlerts} 
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>System Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Receive important system notifications
              </p>
            </div>
            <Switch 
              checked={systemAlerts} 
              onCheckedChange={setSystemAlerts} 
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Weekly Reports</Label>
              <p className="text-sm text-muted-foreground">
                Get weekly analytics reports via email
              </p>
            </div>
            <Switch 
              checked={weeklyReports} 
              onCheckedChange={setWeeklyReports} 
            />
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={logout}>
          Logout
        </Button>
        <Button onClick={handleSaveSettings} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>
    </div>
  );
}




