"use client"

import { AdminErrorBoundary } from "@/components/common/error-boundary"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, SortableTableHead, Pagination, useDataTable } from "@/components/common"
import { useApp } from "@/contexts/app-context"
import { useOrganization } from "@/contexts/organization-context"
import { useToastHelpers } from "@/components/common"
import { useState } from "react"
import { Users, Settings, BarChart3, Shield, Plus, Edit, Trash2 } from "lucide-react"
import { ConfirmationModal } from "@/components/common"

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  created_at: string
}

export default function AdminPage() {
  const { isAuthenticated } = useApp()
  const { userRole, permissions } = useOrganization()
  const { showSuccess, showError } = useToastHelpers()
  
  const [users, setUsers] = useState<User[]>([
    {
      id: "1",
      email: "admin@example.com",
      first_name: "Admin",
      last_name: "User",
      role: "Admin",
      is_active: true,
      created_at: "2024-01-01T00:00:00Z"
    },
    {
      id: "2",
      email: "designer@example.com",
      first_name: "Designer",
      last_name: "User",
      role: "Designer",
      is_active: true,
      created_at: "2024-01-02T00:00:00Z"
    }
  ])
  
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [userToDelete, setUserToDelete] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const {
    data: paginatedUsers,
    sort,
    currentPage,
    totalPages,
    handleSort: handleSortInternal,
    handlePageChange,
  } = useDataTable({
    data: users,
    initialSort: { key: 'created_at', direction: 'desc' },
    initialPageSize: 10,
  })

  // Wrapper function to convert string to keyof User
  const handleSort = (key: string) => {
    handleSortInternal(key as keyof User)
  }

  // Check if user has admin permissions
  const isAdmin = userRole === 'Admin' || permissions.includes('admin_access')
  
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-muted-foreground">Please log in to access the admin panel.</p>
        </div>
      </div>
    )
  }

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
          <p className="text-muted-foreground">You don&apos;t have permission to access the admin panel.</p>
        </div>
      </div>
    )
  }

  const handleDeleteUser = (user: User) => {
    setUserToDelete(user)
    setShowDeleteModal(true)
  }

  const confirmDeleteUser = async () => {
    if (!userToDelete) return

    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setUsers(prev => prev.filter(u => u.id !== userToDelete.id))
      showSuccess("User deleted successfully")
      setShowDeleteModal(false)
      setUserToDelete(null)
    } catch {
      showError("Failed to delete user")
    } finally {
      setIsLoading(false)
    }
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'Admin':
        return 'destructive'
      case 'Manager':
        return 'default'
      case 'Designer':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <AdminErrorBoundary>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Admin Panel</h1>
            <p className="text-muted-foreground">
              Manage users, settings, and organization details.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <Plus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
              <p className="text-xs text-muted-foreground">
                +2 from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(u => u.is_active).length}
              </div>
              <p className="text-xs text-muted-foreground">
                {Math.round((users.filter(u => u.is_active).length / users.length) * 100)}% of total
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Admins</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(u => u.role === 'Admin').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Administrative users
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Designers</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(u => u.role === 'Designer').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Design team members
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>Users Management</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <SortableTableHead
                    sortKey="first_name"
                    currentSort={sort}
                    onSort={handleSort}
                  >
                    Name
                  </SortableTableHead>
                  <SortableTableHead
                    sortKey="email"
                    currentSort={sort}
                    onSort={handleSort}
                  >
                    Email
                  </SortableTableHead>
                  <SortableTableHead
                    sortKey="role"
                    currentSort={sort}
                    onSort={handleSort}
                  >
                    Role
                  </SortableTableHead>
                  <SortableTableHead
                    sortKey="is_active"
                    currentSort={sort}
                    onSort={handleSort}
                  >
                    Status
                  </SortableTableHead>
                  <SortableTableHead
                    sortKey="created_at"
                    currentSort={sort}
                    onSort={handleSort}
                  >
                    Created
                  </SortableTableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">
                      {user.first_name} {user.last_name}
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.is_active ? 'default' : 'secondary'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(user.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteUser(user)}
                          disabled={user.id === "1"} // Prevent deleting the first admin
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            
            {totalPages > 1 && (
              <div className="mt-4">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Delete Confirmation Modal */}
        <ConfirmationModal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          onConfirm={confirmDeleteUser}
          title="Delete User"
          message={`Are you sure you want to delete ${userToDelete?.first_name} ${userToDelete?.last_name}? This action cannot be undone.`}
          confirmText="Delete"
          cancelText="Cancel"
          variant="destructive"
          isLoading={isLoading}
        />
      </div>
    </AdminErrorBoundary>
  )
}
