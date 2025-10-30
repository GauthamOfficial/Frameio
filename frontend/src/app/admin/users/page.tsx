'use client';

import { useState } from 'react';
import { UserTable, User } from '@/components/admin/UserTable';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Download } from 'lucide-react';

export default function AdminUsersPage() {
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data - Replace with real data from your API
  const [users] = useState<User[]>([
    {
      id: '1',
      name: 'John Doe',
      email: 'john.doe@fashiontextiles.com',
      company: 'Fashion Textiles Co.',
      signupDate: '2024-01-15',
      lastActivity: '2 hours ago',
      status: 'active',
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane.smith@modernfabrics.com',
      company: 'Modern Fabrics Ltd.',
      signupDate: '2024-01-20',
      lastActivity: '1 day ago',
      status: 'active',
    },
    {
      id: '3',
      name: 'Mike Johnson',
      email: 'mike.j@elitedesigns.com',
      company: 'Elite Designs Inc.',
      signupDate: '2024-02-05',
      lastActivity: '5 minutes ago',
      status: 'active',
    },
    {
      id: '4',
      name: 'Sarah Williams',
      email: 'sarah.w@textilemasters.com',
      company: 'Textile Masters',
      signupDate: '2024-02-10',
      lastActivity: '3 days ago',
      status: 'inactive',
    },
    {
      id: '5',
      name: 'Tom Brown',
      email: 'tom.brown@fabricinnovations.com',
      company: 'Fabric Innovations',
      signupDate: '2024-02-15',
      lastActivity: '1 week ago',
      status: 'suspended',
    },
    {
      id: '6',
      name: 'Emily Davis',
      email: 'emily.d@cottonworks.com',
      company: 'Cotton Works',
      signupDate: '2024-03-01',
      lastActivity: '30 minutes ago',
      status: 'active',
    },
    {
      id: '7',
      name: 'David Wilson',
      email: 'david.w@silkroad.com',
      company: 'Silk Road Textiles',
      signupDate: '2024-03-05',
      lastActivity: '2 days ago',
      status: 'active',
    },
    {
      id: '8',
      name: 'Lisa Anderson',
      email: 'lisa.a@woolcraft.com',
      company: 'Wool Craft',
      signupDate: '2024-03-10',
      lastActivity: '4 hours ago',
      status: 'active',
    },
  ]);

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
    console.log('Edit user:', user);
    // Implement edit user modal
  };

  const handleDelete = (user: User) => {
    console.log('Delete user:', user);
    // Implement delete confirmation
  };

  const handleExport = () => {
    console.log('Export users data');
    // Implement CSV export
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

          <UserTable
            users={filteredUsers}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </CardContent>
      </Card>
    </div>
  );
}

