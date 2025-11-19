'use client';

import { useAdminAuth } from '@/contexts/admin-auth-context';
import { Button } from '@/components/ui/button';
import { Bell, Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

export function Navbar() {
  const { username } = useAdminAuth();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check if dark mode is enabled
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div>
        <h1 className="text-xl font-semibold">Admin Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Welcome back, {username}
        </p>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
        
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {isDark ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  );
}







