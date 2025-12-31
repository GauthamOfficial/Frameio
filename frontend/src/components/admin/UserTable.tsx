'use client';

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Edit, Trash2, Eye } from 'lucide-react';

export interface User {
  id: string;
  name: string;
  email: string;
  company: string;
  signupDate: string;
  lastActivity: string;
  status: 'active' | 'inactive' | 'suspended';
  subscription_expires_at?: string | null;
  subscription_plan?: 'free' | 'monthly' | 'yearly' | string;
  has_active_subscription?: boolean;
}

interface UserTableProps {
  users: User[];
  onView?: (user: User) => void;
  onEdit?: (user: User) => void;
  onDelete?: (user: User) => void;
  onSuspend?: (user: User) => void;
}

export function UserTable({ users, onView, onEdit, onDelete }: UserTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  const totalPages = Math.ceil(users.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentUsers = users.slice(startIndex, endIndex);

  const getStatusColor = (status: User['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 hover:bg-green-100';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 hover:bg-gray-100';
      case 'suspended':
        return 'bg-red-100 text-red-800 hover:bg-red-100';
      default:
        return 'bg-gray-100 text-gray-800 hover:bg-gray-100';
    }
  };

  const formatSubscriptionStatus = (user: User) => {
    if (user.has_active_subscription && user.subscription_expires_at) {
      const expiresAt = new Date(user.subscription_expires_at);
      const daysUntilExpiry = Math.ceil((expiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      if (daysUntilExpiry <= 7) {
        return { text: `Expires in ${daysUntilExpiry}d`, color: 'bg-yellow-100 text-yellow-800' };
      }
      return { text: 'Active', color: 'bg-blue-100 text-blue-800' };
    }
    return { text: 'Free', color: 'bg-gray-100 text-gray-600' };
  };

  return (
    <div className="space-y-4">
      {/* Desktop Table View */}
      <div className="hidden md:block rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Signup Date</TableHead>
              <TableHead>Last Activity</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Subscription</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {currentUsers.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">{user.name}</TableCell>
                <TableCell className="max-w-[200px] truncate">{user.email}</TableCell>
                <TableCell>{user.company}</TableCell>
                <TableCell className="whitespace-nowrap">{user.signupDate}</TableCell>
                <TableCell className="whitespace-nowrap">{user.lastActivity}</TableCell>
                <TableCell>
                  <Badge className={getStatusColor(user.status)}>
                    {user.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge className={formatSubscriptionStatus(user).color}>
                    {formatSubscriptionStatus(user).text}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    {onView && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onView(user)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                    {onEdit && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onEdit(user)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    )}
                    {onDelete && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onDelete(user)}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-3">
        {currentUsers.map((user) => (
          <div
            key={user.id}
            className="rounded-lg border bg-card p-4 space-y-3 overflow-hidden"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-sm truncate">{user.name}</h3>
                <p className="text-xs text-muted-foreground truncate mt-1">{user.email}</p>
              </div>
              <Badge className={getStatusColor(user.status)}>
                {user.status}
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">Company</p>
                <p className="font-medium truncate">{user.company}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Signup Date</p>
                <p className="font-medium">{user.signupDate}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Last Activity</p>
                <p className="font-medium">{user.lastActivity}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Subscription</p>
                <Badge className={formatSubscriptionStatus(user).color}>
                  {formatSubscriptionStatus(user).text}
                </Badge>
              </div>
            </div>

            <div className="flex gap-1.5 sm:gap-2 pt-2 border-t w-full">
              {onView && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 min-w-0 text-xs sm:text-sm"
                  onClick={() => onView(user)}
                >
                  <Eye className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1" />
                  <span className="truncate">View</span>
                </Button>
              )}
              {onEdit && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 min-w-0 text-xs sm:text-sm"
                  onClick={() => onEdit(user)}
                >
                  <Edit className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1" />
                  <span className="truncate">Edit</span>
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 min-w-0 text-xs sm:text-sm text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={() => onDelete(user)}
                >
                  <Trash2 className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1" />
                  <span className="truncate">Delete</span>
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs sm:text-sm text-muted-foreground text-center sm:text-left">
            Showing {startIndex + 1} to {Math.min(endIndex, users.length)} of {users.length} users
          </p>
          <div className="flex gap-2 w-full sm:w-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="flex-1 sm:flex-initial"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="flex-1 sm:flex-initial"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}









