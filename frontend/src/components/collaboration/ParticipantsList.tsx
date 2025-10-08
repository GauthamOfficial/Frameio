'use client';

import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  User, 
  Crown, 
  Edit, 
  Eye, 
  MoreVertical,
  Video,
  Mic,
  MicOff,
  VideoOff
} from 'lucide-react';

interface Participant {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'editor' | 'viewer';
  isOnline: boolean;
  cursor?: {
    x: number;
    y: number;
  };
  avatar?: string;
  isVideoEnabled?: boolean;
  isAudioEnabled?: boolean;
}

interface ParticipantsListProps {
  participants: Participant[];
}

export function ParticipantsList({ participants }: ParticipantsListProps) {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown className="h-3 w-3 text-yellow-500" />;
      case 'editor':
        return <Edit className="h-3 w-3 text-blue-500" />;
      case 'viewer':
        return <Eye className="h-3 w-3 text-gray-500" />;
      default:
        return <User className="h-3 w-3 text-gray-500" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'editor':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'viewer':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const onlineParticipants = participants.filter(p => p.isOnline);
  const offlineParticipants = participants.filter(p => !p.isOnline);

  return (
    <div className="space-y-4">
      {/* Online Participants */}
      {onlineParticipants.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-sm font-medium">Online ({onlineParticipants.length})</span>
          </div>
          
          <div className="space-y-2">
            {onlineParticipants.map((participant) => (
              <div
                key={participant.id}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="relative">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={participant.avatar} />
                    <AvatarFallback className="text-xs">
                      {getInitials(participant.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white rounded-full" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">
                      {participant.name}
                    </span>
                    {getRoleIcon(participant.role)}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getRoleColor(participant.role)}`}
                    >
                      {participant.role}
                    </Badge>
                    
                    {/* Media Status */}
                    <div className="flex items-center gap-1">
                      {participant.isVideoEnabled ? (
                        <Video className="h-3 w-3 text-green-500" />
                      ) : (
                        <VideoOff className="h-3 w-3 text-gray-400" />
                      )}
                      {participant.isAudioEnabled ? (
                        <Mic className="h-3 w-3 text-green-500" />
                      ) : (
                        <MicOff className="h-3 w-3 text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>
                
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <MoreVertical className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Offline Participants */}
      {offlineParticipants.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full" />
            <span className="text-sm font-medium">Offline ({offlineParticipants.length})</span>
          </div>
          
          <div className="space-y-2">
            {offlineParticipants.map((participant) => (
              <div
                key={participant.id}
                className="flex items-center gap-3 p-2 rounded-lg opacity-60"
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src={participant.avatar} />
                  <AvatarFallback className="text-xs">
                    {getInitials(participant.name)}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">
                      {participant.name}
                    </span>
                    {getRoleIcon(participant.role)}
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${getRoleColor(participant.role)}`}
                  >
                    {participant.role}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invite Button */}
      <div className="pt-4 border-t">
        <Button variant="outline" size="sm" className="w-full">
          <User className="h-4 w-4 mr-2" />
          Invite People
        </Button>
      </div>
    </div>
  );
}
