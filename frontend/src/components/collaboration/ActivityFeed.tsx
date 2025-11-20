'use client';

import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  UserPlus, 
  UserMinus, 
  Edit, 
  MessageSquare, 
  Share2, 
  Clock,
  Activity as ActivityIcon
} from 'lucide-react';

interface Participant {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'editor' | 'viewer';
  isOnline: boolean;
  avatar?: string;
}

interface Activity {
  id: string;
  type: 'join' | 'leave' | 'edit' | 'comment' | 'share';
  user: Participant;
  description: string;
  timestamp: string;
}

interface ActivityFeedProps {
  activities: Activity[];
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'join':
        return <UserPlus className="h-4 w-4 text-green-500" />;
      case 'leave':
        return <UserMinus className="h-4 w-4 text-red-500" />;
      case 'edit':
        return <Edit className="h-4 w-4 text-blue-500" />;
      case 'comment':
        return <MessageSquare className="h-4 w-4 text-purple-500" />;
      case 'share':
        return <Share2 className="h-4 w-4 text-orange-500" />;
      default:
        return <ActivityIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'join':
        return 'bg-green-50 border-green-200';
      case 'leave':
        return 'bg-red-50 border-red-200';
      case 'edit':
        return 'bg-blue-50 border-blue-200';
      case 'comment':
        return 'bg-purple-50 border-purple-200';
      case 'share':
        return 'bg-orange-50 border-orange-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <ActivityIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No activity yet</p>
        <p className="text-sm">Activity will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className={`flex gap-3 p-3 rounded-lg border ${getActivityColor(activity.type)}`}
        >
          <div className="flex-shrink-0">
            <Avatar className="h-8 w-8">
              <AvatarImage src={activity.user.avatar} />
              <AvatarFallback className="text-xs">
                {getInitials(activity.user.name)}
              </AvatarFallback>
            </Avatar>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">
                    {activity.user.name}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {activity.user.role}
                  </Badge>
                </div>
                
                <p className="text-sm text-gray-700">
                  {activity.description}
                </p>
                
                <div className="flex items-center gap-1 mt-1">
                  <Clock className="h-3 w-3 text-gray-400" />
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(activity.timestamp)}
                  </span>
                </div>
              </div>
              
              <div className="flex-shrink-0">
                {getActivityIcon(activity.type)}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
