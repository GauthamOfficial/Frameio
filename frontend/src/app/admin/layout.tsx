'use client';

import { AdminAuthProvider } from '@/contexts/admin-auth-context';
import { Sidebar } from '@/components/admin/Sidebar';
import { Navbar } from '@/components/admin/Navbar';
import { useAdminAuth } from '@/contexts/admin-auth-context';
import { Loader2 } from 'lucide-react';
import { usePathname } from 'next/navigation';

function AdminLayoutContent({ children }: { children: React.ReactNode }) {
  const { isLoading, isAuthenticated } = useAdminAuth();
  const pathname = usePathname();
  
  // Don't wrap login page with admin layout
  if (pathname === '/admin/login') {
    return <>{children}</>;
  }

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return <>{children}</>;
  }

  // Show admin dashboard with sidebar/navbar for authenticated users
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AdminAuthProvider>
      <AdminLayoutContent>{children}</AdminLayoutContent>
    </AdminAuthProvider>
  );
}

