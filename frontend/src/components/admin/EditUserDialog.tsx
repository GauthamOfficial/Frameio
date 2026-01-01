'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { User } from './UserTable';

interface EditUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: User | null;
  onSave: (user: User) => Promise<void>;
}

export function EditUserDialog({ open, onOpenChange, user, onSave }: EditUserDialogProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    status: 'active' as User['status'],
    subscription_plan: 'free' as 'free' | 'monthly' | 'yearly',
    subscription_expires_at: null as string | null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      // Format subscription_expires_at for datetime-local input
      let expiresAt = null;
      if (user.subscription_expires_at) {
        const date = new Date(user.subscription_expires_at);
        // Convert to local datetime string (YYYY-MM-DDTHH:mm)
        expiresAt = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
          .toISOString()
          .slice(0, 16);
      }
      
      setFormData({
        name: user.name,
        email: user.email,
        company: user.company,
        status: user.status,
        subscription_plan: (user.subscription_plan as 'free' | 'monthly' | 'yearly') || 'free',
        subscription_expires_at: expiresAt,
      });
      setError(null);
    }
  }, [user]);

  const extendSubscription = (months: number) => {
    const now = new Date();
    const currentExpiry = formData.subscription_expires_at 
      ? new Date(formData.subscription_expires_at)
      : now;
    
    // If current expiry is in the past, start from now, otherwise extend from current expiry
    const baseDate = currentExpiry > now ? currentExpiry : now;
    const newExpiry = new Date(baseDate);
    newExpiry.setMonth(newExpiry.getMonth() + months);
    
    // Format for datetime-local input
    const formattedDate = new Date(newExpiry.getTime() - newExpiry.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
    
    setFormData({
      ...formData,
      subscription_expires_at: formattedDate,
      subscription_plan: months === 12 ? 'yearly' : 'monthly',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      // Convert datetime-local value back to ISO string for backend
      let expiresAtISO = null;
      if (formData.subscription_expires_at) {
        expiresAtISO = new Date(formData.subscription_expires_at).toISOString();
      }
      
      await onSave({
        ...user,
        ...formData,
        subscription_expires_at: expiresAtISO,
      });
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg w-[calc(100%-2rem)] sm:w-full mx-4 max-h-[90vh] flex flex-col">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader className="flex-shrink-0">
          <div className="text-lg sm:text-xl">
            <DialogTitle>Edit User</DialogTitle>
          </div>
          <div className="text-sm">
            <DialogDescription>
              Update user information below. Click save when you&apos;re done.
            </DialogDescription>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
          <div className="space-y-4 overflow-y-auto flex-1 pr-2">
            <div>
              <Label htmlFor="name" className="text-sm">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-sm">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="company" className="text-sm">Company</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="status" className="text-sm">Status</Label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as User['status'] })}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 mt-1"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>

            <div className="border-t pt-4 space-y-4">
              <div>
                <Label className="text-sm font-semibold">Subscription Management</Label>
                <p className="text-xs text-muted-foreground mt-1">
                  Set subscription expiration to grant unlimited access until that date
                </p>
              </div>

              <div>
                <Label htmlFor="subscription_plan" className="text-sm">Subscription Plan</Label>
                <select
                  id="subscription_plan"
                  value={formData.subscription_plan}
                  onChange={(e) => setFormData({ ...formData, subscription_plan: e.target.value as 'free' | 'monthly' | 'yearly' })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 mt-1"
                >
                  <option value="free">Free</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div>
                <Label htmlFor="subscription_expires_at" className="text-sm">Subscription Expires At</Label>
                <Input
                  id="subscription_expires_at"
                  type="datetime-local"
                  value={formData.subscription_expires_at || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value) {
                      setFormData({ ...formData, subscription_expires_at: value });
                    } else {
                      setFormData({ ...formData, subscription_expires_at: null });
                    }
                  }}
                  className="mt-1"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Leave empty to remove subscription access
                </p>
              </div>

              <div>
                <Label className="text-sm">Quick Extend</Label>
                <div className="flex gap-2 mt-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => extendSubscription(1)}
                    className="flex-1"
                  >
                    +1 Month
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => extendSubscription(3)}
                    className="flex-1"
                  >
                    +3 Months
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => extendSubscription(12)}
                    className="flex-1"
                  >
                    +1 Year
                  </Button>
                </div>
              </div>
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded break-words">
                {error}
              </div>
            )}
          </div>

          <DialogFooter className="flex-shrink-0 pt-4 border-t mt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="w-full sm:w-auto">
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}








