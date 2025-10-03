"use client"

import { useState, useEffect } from 'react'
import { useUser, useAuth } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { useOrganization } from "@/contexts/organization-context"
import { userApi, User } from "@/lib/api"
import { 
  Users, 
  Search, 
  Plus, 
  MoreVertical, 
  Edit, 
  Trash2,
  UserPlus,
  Shield,
  UserCheck,
  Palette
} from "lucide-react"
import { cn } from "@/lib/utils"

export default function UsersPage() {
  const { user } = useUser()
  const { getToken } = useAuth()
  const { userRole, permissions, isLoading: orgLoading } = useOrganization()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showRoleModal, setShowRoleModal] = useState(false)
  const [newRole, setNewRole] = useState<string>('')

  // Check if user has permission to access this page
  if (!orgLoading && !permissions.includes('manage_users')) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Access Denied</h2>
          <p className="text-muted-foreground">
            You don't have permission to manage users
          </p>
        </div>
      </div>
    )
  }

  const fetchUsers = async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)
      const token = await getToken()
      const usersData = await userApi.getUsers(token)
      setUsers(usersData)
    } catch (err) {
      console.error('Failed to fetch users:', err)
      setError('Failed to load')
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = async (userId: string, role: string) => {
    if (!user) return

    try {
      const token = await getToken()
      await userApi.updateUserRole(userId, role, token)
      await fetchUsers() // Refresh the list
      setShowRoleModal(false)
      setSelectedUser(null)
    } catch (err) {
      console.error('Failed to update user role:', err)
      setError('Failed to update user role')
    }
  }

  const handleRemoveUser = async (userId: string) => {
    if (!user) return

    try {
      const token = await getToken()
      await userApi.removeUser(userId, token)
      await fetchUsers() // Refresh the list
    } catch (err) {
      console.error('Failed to remove user:', err)
      setError('Failed to remove user')
    }
  }

  const handleInviteUser = async (email: string, role: string) => {
    if (!user) return

    try {
      const token = await getToken()
      await userApi.inviteUser(email, role, token)
      await fetchUsers() // Refresh the list
    } catch (err) {
      console.error('Failed to invite user:', err)
      setError('Failed to invite user')
    }
  }

  useEffect(() => {
    if (user && permissions.includes('manage_users')) {
      fetchUsers()
    }
  }, [user, permissions])

  const filteredUsers = users.filter(user => 
    user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

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

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'Admin':
        return <Shield className="h-4 w-4" />
      case 'Manager':
        return <UserCheck className="h-4 w-4" />
      case 'Designer':
        return <Palette className="h-4 w-4" />
      default:
        return <Users className="h-4 w-4" />
    }
  }

  if (loading || orgLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">User Management</h1>
            <p className="text-muted-foreground mt-1">
              Manage users and their roles in your organization.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <UserPlus className="mr-2 h-4 w-4" />
            Invite User
          </Button>
        </div>

        {/* Search and Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-chart-1" />
                <div>
                  <p className="text-2xl font-bold">{users.length}</p>
                  <p className="text-xs text-muted-foreground">Total Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-chart-2" />
                <div>
                  <p className="text-2xl font-bold">
                    {users.filter(u => u.role === 'Admin').length}
                  </p>
                  <p className="text-xs text-muted-foreground">Admins</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <UserCheck className="h-5 w-5 text-chart-3" />
                <div>
                  <p className="text-2xl font-bold">
                    {users.filter(u => u.role === 'Manager').length}
                  </p>
                  <p className="text-xs text-muted-foreground">Managers</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="textile-hover textile-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Palette className="h-5 w-5 text-chart-4" />
                <div>
                  <p className="text-2xl font-bold">
                    {users.filter(u => u.role === 'Designer').length}
                  </p>
                  <p className="text-xs text-muted-foreground">Designers</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <Card className="textile-hover textile-shadow">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Organization Users</CardTitle>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-destructive text-sm">{error}</p>
              </div>
            )}
            
            <div className="space-y-4">
              {filteredUsers.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                      <span className="text-primary-foreground font-semibold">
                        {user.first_name[0]}{user.last_name[0]}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">
                        {user.first_name} {user.last_name}
                      </p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Badge 
                      variant={getRoleBadgeVariant(user.role)}
                      className="flex items-center space-x-1"
                    >
                      {getRoleIcon(user.role)}
                      <span>{user.role}</span>
                    </Badge>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedUser(user)
                          setNewRole(user.role)
                          setShowRoleModal(true)
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveUser(user.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredUsers.length === 0 && (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    {searchTerm ? 'No users found matching your search.' : 'No users found.'}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Role Change Modal */}
        {showRoleModal && selectedUser && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md textile-shadow">
              <CardHeader>
                <CardTitle>Change User Role</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-2">
                    Changing role for: {selectedUser.first_name} {selectedUser.last_name}
                  </p>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full p-2 border border-border rounded-lg bg-input"
                  >
                    <option value="Designer">Designer</option>
                    <option value="Manager">Manager</option>
                    <option value="Admin">Admin</option>
                  </select>
                </div>
                <div className="flex space-x-2">
                  <Button
                    onClick={() => handleRoleChange(selectedUser.id, newRole)}
                    className="flex-1"
                  >
                    Update Role
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowRoleModal(false)
                      setSelectedUser(null)
                    }}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
  )
}
