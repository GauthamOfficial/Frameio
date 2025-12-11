'use client';

import { useState, useEffect } from 'react';
import { UserTable, User } from '@/components/admin/UserTable';
import { EditUserDialog } from '@/components/admin/EditUserDialog';
import { DeleteUserDialog } from '@/components/admin/DeleteUserDialog';
import { Toast } from '@/components/ui/toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Download, Loader2 } from 'lucide-react';

interface DjangoUser {
  id: string | number;
  email: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  is_active?: boolean;
  date_joined?: string;
  last_login?: string;
}

export default function AdminUsersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  // Real data from Django API - no fallback data
  const [users, setUsers] = useState<User[]>([]);

  // Fetch users from API on mount
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('[Admin Users] Fetching users from /api/admin/users');
      let response: Response;
      try {
        response = await fetch('/api/admin/users', {
          method: 'GET',
          credentials: 'include',
        });
      } catch (networkError) {
        // Handle network errors (frontend API route not accessible)
        const errorMessage = networkError instanceof Error ? networkError.message : 'Network error';
        console.warn('[Admin Users] Network error:', errorMessage);
        setError('Unable to connect to the server. Please check your connection and try again.');
        setUsers([]);
        setLoading(false);
        return;
      }

      console.log('[Admin Users] Response status:', response.status);

      if (!response.ok) {
        let errorData: Record<string, unknown> = {};
        try {
          const text = await response.text();
          if (text) {
            errorData = JSON.parse(text);
          }
        } catch {
          // If response is not JSON, use status text
          errorData = { error: response.statusText || 'Unknown error' };
        }
        
        console.warn('[Admin Users] Error response:', errorData);
        
        // Provide more helpful error messages
        if (response.status === 401 || response.status === 403) {
          const errorMessage = (typeof errorData.error === 'string' ? errorData.error : null) || 
                               (typeof errorData.detail === 'string' ? errorData.detail : null) || 
                               'Authentication required. Please log in to the admin panel.';
          setError(errorMessage);
          setUsers([]);
          setLoading(false);
          return;
        }
        
        // Handle backend unavailable errors
        if (response.status === 503 || errorData.networkError) {
          const errorMessage = (typeof errorData.detail === 'string' ? errorData.detail : null) || 
                               (typeof errorData.error === 'string' ? errorData.error : null) || 
                               'Backend service is unavailable. Please ensure the backend server is running.';
          setError(errorMessage);
          setUsers([]);
          setLoading(false);
          return;
        }
        
        // For other errors
        const errorMessage = (typeof errorData.error === 'string' ? errorData.error : null) || 
                             (typeof errorData.detail === 'string' ? errorData.detail : null) || 
                             (typeof errorData.message === 'string' ? errorData.message : null) || 
                             `Failed to load users (${response.status})`;
          setError(errorMessage);
        setUsers([]);
        setLoading(false);
        return;
      }

      let data: Record<string, unknown>;
      try {
        const text = await response.text();
        if (!text) {
          console.warn('[Admin Users] Empty response');
          setUsers([]);
          setLoading(false);
          return;
        }
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('[Admin Users] Failed to parse response:', parseError);
        setError('Invalid response from server');
        setUsers([]);
        setLoading(false);
        return;
      }
      console.log('[Admin Users] Response data:', data);
      
      // Handle both array and paginated response formats
      let djangoUsers: DjangoUser[] = [];
      if (Array.isArray(data)) {
        console.log('[Admin Users] Data is an array with', data.length, 'users');
        djangoUsers = data;
      } else if (data.results && Array.isArray(data.results)) {
        // Paginated response from Django REST Framework
        console.log('[Admin Users] Paginated response with', data.results.length, 'users');
        djangoUsers = data.results;
      } else if (data.data && Array.isArray(data.data)) {
        // Alternative format
        console.log('[Admin Users] Data.data format with', data.data.length, 'users');
        djangoUsers = data.data;
      } else {
        console.error('[Admin Users] Unexpected API response format:', data);
        setError('Invalid response format from API. Please contact support.');
        setUsers([]);
        setLoading(false);
        return;
      }
      
      // Transform Django users to our User interface
      const transformedUsers: User[] = djangoUsers.map(du => ({
        id: String(du.id),
        name: `${du.first_name || ''} ${du.last_name || ''}`.trim() || du.username || du.email,
        email: du.email,
        company: 'N/A', // Django doesn't have company in User model
        signupDate: du.date_joined ? new Date(du.date_joined).toLocaleDateString() : 'N/A',
        lastActivity: du.last_login ? new Date(du.last_login).toLocaleDateString() : 'Never',
        status: du.is_active ? 'active' : 'inactive',
      }));

      console.log('[Admin Users] Loaded users:', transformedUsers.length);
      console.log('[Admin Users] Sample user IDs:', transformedUsers.slice(0, 3).map(u => u.id));
      
      if (transformedUsers.length === 0) {
        console.warn('[Admin Users] No users loaded from API!');
        setError('No users found in the database. The API returned an empty list.');
        setUsers([]); // Clear any existing data
      } else {
        setUsers(transformedUsers);
      }
    } catch (err) {
      console.error('[Admin Users] Error loading users:', err);
      setError(err instanceof Error ? err.message : 'Failed to load users');
      setUsers([]); // Clear users on error - no fallback data
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleView = (user: User) => {
    console.log('View user:', user);
    // Implement view user details modal
  };

  const handleEdit = (user: User) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };

  const handleDelete = (user: User) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const handleSaveUser = async (updatedUser: User) => {
    try {
      // Use Next.js API proxy route that handles admin authentication
      const response = await fetch(`/api/admin/users/${updatedUser.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: updatedUser.name.split(' ')[0] || updatedUser.name,
          last_name: updatedUser.name.split(' ').slice(1).join(' ') || '',
          // Note: email and status updates may require different endpoints
          // This updates basic user profile fields
        }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || errorData.message || `Failed to update user: ${response.statusText}`);
      }

      // Reload users to get fresh data
      await loadUsers();
      
      // Show success message
      setToast({
        message: `User ${updatedUser.name} updated successfully!`,
        type: 'success'
      });
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  };

  const handleConfirmDelete = async (userToDelete: User) => {
    try {
      console.log('[Admin Users] Attempting to delete user:', userToDelete);
      console.log('[Admin Users] User ID:', userToDelete.id);
      
      // Use Next.js API proxy route that handles admin authentication
      const response = await fetch(`/api/admin/users/${userToDelete.id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      console.log('[Admin Users] Delete response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || errorData.message || `Failed to delete user: ${response.statusText}`);
      }

      // Reload users to get fresh data
      await loadUsers();
      
      // Show success message
      setToast({
        message: `User ${userToDelete.name} deleted successfully!`,
        type: 'success'
      });
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  };

  const handleExport = () => {
    console.log('Export users data');
    // Implement CSV export
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Users Management</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Manage and monitor all platform users
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <Button variant="outline" onClick={handleExport} className="w-full sm:w-auto">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button className="w-full sm:w-auto">
            <Plus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <Card>
          <CardContent className="flex items-center justify-center py-12 px-4">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            <span className="ml-2 text-sm sm:text-base text-gray-600">Loading users...</span>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-6 px-4 sm:px-6">
            <p className="text-sm sm:text-base text-red-600 font-semibold break-words">Error: {error}</p>
            <p className="text-xs sm:text-sm text-red-500 mt-2">
              Check your browser console (F12) for detailed error messages.
            </p>
            <div className="mt-4 flex flex-col sm:flex-row gap-2">
              <Button onClick={loadUsers} className="w-full sm:w-auto">
                Try Again
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  console.log('Current state:', { users, loading, error });
                  console.log('Attempting to reload...');
                  loadUsers();
                }}
                className="w-full sm:w-auto"
              >
                Reload with Logging
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Source Indicator */}
      {!loading && !error && users.length > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="py-4 px-4 sm:px-6">
            <p className="text-xs sm:text-sm">
              ✓ Showing {users.length} users from the database
            </p>
            <p className="text-xs text-gray-600 mt-1 break-all">
              Sample IDs: {users.slice(0, 2).map(u => u.id.substring(0, 8)).join(', ')}...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      {!loading && !error && (
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2 px-4 sm:px-6 pt-4 sm:pt-6">
            <CardDescription className="text-xs sm:text-sm">Total Users</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{users.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 px-4 sm:px-6 pt-4 sm:pt-6">
            <CardDescription className="text-xs sm:text-sm">Active Users</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">
              {users.filter((u) => u.status === 'active').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 px-4 sm:px-6 pt-4 sm:pt-6">
            <CardDescription className="text-xs sm:text-sm">Inactive Users</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">
              {users.filter((u) => u.status === 'inactive').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2 px-4 sm:px-6 pt-4 sm:pt-6">
            <CardDescription className="text-xs sm:text-sm">Suspended Users</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">
              {users.filter((u) => u.status === 'suspended').length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>
      )}

      {/* Empty State */}
      {!loading && !error && users.length === 0 && (
        <Card>
          <CardContent className="py-12 px-4 text-center">
            <p className="text-gray-500 text-base sm:text-lg mb-4">No users found in the database</p>
            <p className="text-xs sm:text-sm text-gray-400">
              Users will appear here once they are added to the system.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Search and Filter */}
      {!loading && !error && users.length > 0 && (
        <Card>
        <CardHeader className="px-4 sm:px-6 pt-6">
          <CardTitle className="text-lg sm:text-xl">All Users</CardTitle>
          <CardDescription className="text-sm">
            Search and manage user accounts ({users.length} total)
          </CardDescription>
        </CardHeader>
        <CardContent className="px-4 sm:px-6 pb-6">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name, email, or company..."
                className="pl-10 text-sm sm:text-base"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {filteredUsers.length === 0 ? (
            <div className="text-center py-8 text-sm sm:text-base text-gray-500 px-4">
              No users match your search criteria
            </div>
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
      )}

      {/* Edit User Dialog */}
      <EditUserDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        user={selectedUser}
        onSave={handleSaveUser}
      />

      {/* Delete User Dialog */}
      <DeleteUserDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        user={selectedUser}
        onConfirm={handleConfirmDelete}
      />

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

