'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { API_BASE_URL } from '@/lib/config';
import { UserTable, User } from '@/components/admin/UserTable';
import { UserDetailsModal } from '@/components/admin/UserDetailsModal';
import { UserEditModal } from '@/components/admin/UserEditModal';
import { UserDeleteDialog } from '@/components/admin/UserDeleteDialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function AdminUsersPage() {
  const { getToken } = useAuth();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [viewUser, setViewUser] = useState<User | null>(null);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [deleteUser, setDeleteUser] = useState<User | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadUsers() {
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
        const res = await fetch(`${API_BASE_URL}/api/users/`, {
          cache: 'no-store',
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...devHeaders
          }
        });
        if (!res.ok) throw new Error('Failed to fetch users');
        const data = await res.json();
        if (!isMounted) return;
        const list = Array.isArray(data) ? data : data?.results || [];
        // Best-effort mapping to table User shape
        const mapped: User[] = list.map((u: any) => ({
          id: String(u.id ?? u.uuid ?? u.pk ?? Math.random()),
          name: [u.first_name, u.last_name].filter(Boolean).join(' ') || u.name || u.username || u.email || 'Unknown',
          email: u.email || u.username || '',
          company: u.organization?.name || u.company?.name || u.company || '',
          signupDate: u.date_joined || u.created_at || '',
          lastActivity: u.last_login || u.last_activity || '',
          status: (u.status || u.is_active ? (u.is_active ? 'active' : 'inactive') : 'active') as User['status']
        }));
        setUsers(mapped);
      } catch (e: any) {
        if (isMounted) setError(e?.message || 'Failed to load users');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadUsers();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleView = (user: User) => {
    setViewUser(user);
  };

  const handleEdit = (user: User) => {
    setEditUser(user);
  };

  const handleDelete = (user: User) => {
    setDeleteUser(user);
  };

  const handleSaveUser = async (userId: string, updates: Partial<User>) => {
    const token = (await getToken()) || 'test_clerk_token';
    const devHeaders = process.env.NODE_ENV !== 'production'
      ? { 
          'X-Dev-User-Id': '684af5c8-5dd6-4c20-911c-3c8c39a5ca86', 
          'X-Dev-Org-Id': '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb' 
        }
      : {};
    
    const res = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
      method: 'PATCH',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...devHeaders
      },
      body: JSON.stringify(updates)
    });

    if (!res.ok) throw new Error('Failed to update user');

    // Update local state
    setUsers(users.map(u => u.id === userId ? { ...u, ...updates } : u));
    
    toast({
      title: 'Success',
      description: 'User updated successfully',
    });
  };

  const handleConfirmDelete = async (userId: string) => {
    const token = (await getToken()) || 'test_clerk_token';
    const devHeaders = process.env.NODE_ENV !== 'production'
      ? { 
          'X-Dev-User-Id': '684af5c8-5dd6-4c20-911c-3c8c39a5ca86', 
          'X-Dev-Org-Id': '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb' 
        }
      : {};
    
    const res = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
      method: 'DELETE',
      headers: { 
        Authorization: `Bearer ${token}`,
        ...devHeaders
      }
    });

    if (!res.ok) throw new Error('Failed to delete user');

    // Update local state
    setUsers(users.filter(u => u.id !== userId));
    
    toast({
      title: 'Success',
      description: 'User deleted successfully',
    });
  };

  const handleExport = () => {
    // Export users to CSV
    const csv = [
      ['Name', 'Email', 'Company', 'Signup Date', 'Last Activity', 'Status'].join(','),
      ...users.map(u => [u.name, u.email, u.company, u.signupDate, u.lastActivity, u.status].join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `users-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Success',
      description: 'Users exported to CSV',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Users Management</h1>
          <p className="text-muted-foreground">
            Manage and monitor all platform users
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
          <CardDescription>Total Users</CardDescription>
          <CardTitle className="text-3xl">{users.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Users</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.status === 'active').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Inactive Users</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.status === 'inactive').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Suspended Users</CardDescription>
            <CardTitle className="text-3xl">
              {users.filter((u) => u.status === 'suspended').length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>
            Search and manage user accounts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name, email, or company..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="mb-4 text-sm text-red-600">{error}</div>
          )}
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading users...</div>
          ) : (
            <UserTable
              users={filteredUsers}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          )}
        </CardContent>
      </Card>

      {/* Modals */}
      <UserDetailsModal
        user={viewUser}
        open={!!viewUser}
        onOpenChange={(open) => !open && setViewUser(null)}
      />
      
      <UserEditModal
        user={editUser}
        open={!!editUser}
        onOpenChange={(open) => !open && setEditUser(null)}
        onSave={handleSaveUser}
      />
      
      <UserDeleteDialog
        user={deleteUser}
        open={!!deleteUser}
        onOpenChange={(open) => !open && setDeleteUser(null)}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
}

