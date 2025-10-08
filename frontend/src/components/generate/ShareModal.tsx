'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Share2, 
  Copy, 
  Mail, 
  Link, 
  Lock, 
  Globe, 
  Users, 
  Clock,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface ShareModalProps {
  poster: {
    id: string;
    imageUrl: string;
    prompt: string;
  };
  onClose: () => void;
  onShare: (shareData: any) => void;
  isLoading: boolean;
}

interface ShareSettings {
  shareType: 'public' | 'private' | 'organization';
  permissions: {
    canView: boolean;
    canEdit: boolean;
    canComment: boolean;
    canExport: boolean;
  };
  expiresAt?: string;
  password?: string;
  message?: string;
}

export function ShareModal({ poster, onClose, onShare, isLoading }: ShareModalProps) {
  const [shareSettings, setShareSettings] = useState<ShareSettings>({
    shareType: 'private',
    permissions: {
      canView: true,
      canEdit: false,
      canComment: true,
      canExport: false
    }
  });
  
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'viewer' | 'editor' | 'admin'>('viewer');
  const [inviteMessage, setInviteMessage] = useState('');
  const [shareStatus, setShareStatus] = useState<'idle' | 'sharing' | 'success' | 'error'>('idle');
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const shareTypes = [
    {
      id: 'public',
      name: 'Public',
      description: 'Anyone with the link can view',
      icon: <Globe className="h-5 w-5" />,
      color: 'text-green-600'
    },
    {
      id: 'organization',
      name: 'Organization',
      description: 'Only members of your organization',
      icon: <Users className="h-5 w-5" />,
      color: 'text-blue-600'
    },
    {
      id: 'private',
      name: 'Private',
      description: 'Only people you invite',
      icon: <Lock className="h-5 w-5" />,
      color: 'text-gray-600'
    }
  ];

  const roles = [
    {
      id: 'viewer',
      name: 'Viewer',
      description: 'Can view and comment',
      permissions: ['view', 'comment']
    },
    {
      id: 'editor',
      name: 'Editor',
      description: 'Can view, edit, and comment',
      permissions: ['view', 'edit', 'comment']
    },
    {
      id: 'admin',
      name: 'Admin',
      description: 'Full access including sharing',
      permissions: ['view', 'edit', 'comment', 'export', 'share']
    }
  ];

  const handleShare = async () => {
    setShareStatus('sharing');
    try {
      const result = await onShare(shareSettings);
      if (result.success) {
        setShareUrl(result.data?.share_url || '');
        setShareStatus('success');
      } else {
        setShareStatus('error');
      }
    } catch (error) {
      setShareStatus('error');
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;
    
    setShareStatus('sharing');
    try {
      const result = await onShare({
        ...shareSettings,
        inviteEmail,
        inviteRole,
        inviteMessage
      });
      
      if (result.success) {
        setShareStatus('success');
        setInviteEmail('');
        setInviteMessage('');
      } else {
        setShareStatus('error');
      }
    } catch (error) {
      setShareStatus('error');
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const updatePermission = (permission: keyof ShareSettings['permissions'], value: boolean) => {
    setShareSettings(prev => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [permission]: value
      }
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            Share Design
          </CardTitle>
          <CardDescription>
            Share your design with others and collaborate
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Share Type */}
          <div className="space-y-3">
            <Label>Share Type</Label>
            <div className="grid grid-cols-1 gap-3">
              {shareTypes.map((type) => (
                <div
                  key={type.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    shareSettings.shareType === type.id 
                      ? 'ring-2 ring-primary border-primary' 
                      : 'hover:border-primary/50'
                  }`}
                  onClick={() => setShareSettings(prev => ({ ...prev, shareType: type.id as any }))}
                >
                  <div className="flex items-center gap-3">
                    <div className={type.color}>
                      {type.icon}
                    </div>
                    <div>
                      <div className="font-medium">{type.name}</div>
                      <p className="text-sm text-muted-foreground">
                        {type.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Permissions */}
          <div className="space-y-3">
            <Label>Permissions</Label>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="canView"
                    checked={shareSettings.permissions.canView}
                    onChange={(e) => updatePermission('canView', e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="canView">Can view</Label>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="canEdit"
                    checked={shareSettings.permissions.canEdit}
                    onChange={(e) => updatePermission('canEdit', e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="canEdit">Can edit</Label>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="canComment"
                    checked={shareSettings.permissions.canComment}
                    onChange={(e) => updatePermission('canComment', e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="canComment">Can comment</Label>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="canExport"
                    checked={shareSettings.permissions.canExport}
                    onChange={(e) => updatePermission('canExport', e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="canExport">Can export</Label>
                </div>
              </div>
            </div>
          </div>

          {/* Expiration */}
          <div className="space-y-3">
            <Label>Expiration (Optional)</Label>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <Input
                type="datetime-local"
                value={shareSettings.expiresAt || ''}
                onChange={(e) => setShareSettings(prev => ({ 
                  ...prev, 
                  expiresAt: e.target.value 
                }))}
              />
            </div>
          </div>

          {/* Password Protection */}
          {shareSettings.shareType === 'public' && (
            <div className="space-y-3">
              <Label>Password Protection (Optional)</Label>
              <Input
                type="password"
                placeholder="Enter password to protect the link"
                value={shareSettings.password || ''}
                onChange={(e) => setShareSettings(prev => ({ 
                  ...prev, 
                  password: e.target.value 
                }))}
              />
            </div>
          )}

          {/* Invite Members */}
          <div className="space-y-3">
            <Label>Invite Members</Label>
            <div className="space-y-3">
              <div>
                <Label className="text-sm">Email Address</Label>
                <Input
                  type="email"
                  placeholder="Enter email address"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
              </div>
              
              <div>
                <Label className="text-sm">Role</Label>
                <div className="grid grid-cols-3 gap-2">
                  {roles.map((role) => (
                    <Button
                      key={role.id}
                      variant={inviteRole === role.id ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setInviteRole(role.id as any)}
                    >
                      {role.name}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div>
                <Label className="text-sm">Message (Optional)</Label>
                <Textarea
                  placeholder="Add a personal message..."
                  value={inviteMessage}
                  onChange={(e) => setInviteMessage(e.target.value)}
                  rows={2}
                />
              </div>
              
              <Button
                onClick={handleInvite}
                disabled={!inviteEmail.trim() || isLoading}
                className="w-full"
                variant="outline"
              >
                <Mail className="mr-2 h-4 w-4" />
                Send Invitation
              </Button>
            </div>
          </div>

          {/* Share URL */}
          {shareUrl && (
            <div className="space-y-3">
              <Label>Share Link</Label>
              <div className="flex gap-2">
                <Input
                  value={shareUrl}
                  readOnly
                  className="flex-1"
                />
                <Button
                  onClick={copyToClipboard}
                  variant="outline"
                  size="sm"
                >
                  {copied ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Status */}
          {shareStatus === 'sharing' && (
            <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span className="text-sm text-blue-600">Sharing your design...</span>
            </div>
          )}

          {shareStatus === 'success' && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600">Design shared successfully!</span>
            </div>
          )}

          {shareStatus === 'error' && (
            <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <span className="text-sm text-red-600">Failed to share. Please try again.</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleShare}
              disabled={isLoading || shareStatus === 'sharing'}
              className="flex-1"
            >
              {shareStatus === 'sharing' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sharing...
                </>
              ) : (
                <>
                  <Share2 className="mr-2 h-4 w-4" />
                  Create Share Link
                </>
              )}
            </Button>
            <Button onClick={onClose} variant="outline">
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
