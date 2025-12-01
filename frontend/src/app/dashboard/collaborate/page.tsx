'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, 
  MessageSquare, 
  Clock, 
  Send, 
  Video, 
  Mic, 
  MicOff,
  VideoOff,
  Share2,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useAuth, useUser } from '@clerk/nextjs';
import { useCollaboration } from '@/hooks/useCollaboration';
import { useSocket } from '@/hooks/useSocket';
import { CollaborationCanvas } from '@/components/collaboration/CollaborationCanvas';
import { CommentsPanel } from '@/components/collaboration/CommentsPanel';
import { ParticipantsList } from '@/components/collaboration/ParticipantsList';
import { ActivityFeed } from '@/components/collaboration/ActivityFeed';

interface CollaborationSession {
  id: string;
  designId: string;
  participants: Participant[];
  isActive: boolean;
  createdAt: string;
}

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
}

interface Comment {
  id: string;
  content: string;
  author: Participant;
  position?: {
    x: number;
    y: number;
  };
  createdAt: string;
  replies?: Comment[];
}

interface Activity {
  id: string;
  type: 'join' | 'leave' | 'edit' | 'comment' | 'share';
  user: Participant;
  description: string;
  timestamp: string;
}

export default function CollaborationPage() {
  const { userId } = useAuth();
  const { user } = useUser();
  const [session, setSession] = useState<CollaborationSession | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { 
    addComment
  } = useCollaboration();

  const { 
    socket, 
    isConnected, 
    joinSession, 
    leaveSession,
    sendCursorUpdate,
    sendDesignUpdate
  } = useSocket();

  // Mock data for demonstration
  useEffect(() => {
    const mockParticipants: Participant[] = [
      {
        id: userId || '1',
        name: user?.fullName || 'You',
        email: user?.primaryEmailAddress?.emailAddress || 'you@example.com',
        role: 'owner',
        isOnline: true,
        avatar: user?.imageUrl
      },
      {
        id: '2',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'editor',
        isOnline: true,
        cursor: { x: 100, y: 200 }
      },
      {
        id: '3',
        name: 'Jane Smith',
        email: 'jane@example.com',
        role: 'viewer',
        isOnline: false
      }
    ];

    const mockComments: Comment[] = [
      {
        id: '1',
        content: 'Great design! Maybe we should adjust the colors?',
        author: mockParticipants[1],
        position: { x: 150, y: 100 },
        createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        replies: [
          {
            id: '2',
            content: 'I agree, the blue could be more vibrant',
            author: mockParticipants[0],
            createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString()
          }
        ]
      }
    ];

    const mockActivities: Activity[] = [
      {
        id: '1',
        type: 'join',
        user: mockParticipants[1],
        description: 'joined the collaboration',
        timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
      },
      {
        id: '2',
        type: 'edit',
        user: mockParticipants[1],
        description: 'modified the text layer',
        timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString()
      },
      {
        id: '3',
        type: 'comment',
        user: mockParticipants[1],
        description: 'added a comment',
        timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString()
      }
    ];

    setParticipants(mockParticipants);
    setComments(mockComments);
    setActivities(mockActivities);
    setIsLoading(false);
  }, [userId, user]);

  // Socket event handlers
  useEffect(() => {
    if (!socket) return;

    const handleParticipantJoined = (participant: Participant) => {
      setParticipants(prev => {
        const exists = prev.find(p => p.id === participant.id);
        if (exists) {
          return prev.map(p => p.id === participant.id ? { ...p, isOnline: true } : p);
        }
        return [...prev, participant];
      });

      setActivities(prev => [{
        id: Date.now().toString(),
        type: 'join',
        user: participant,
        description: 'joined the collaboration',
        timestamp: new Date().toISOString()
      }, ...prev]);
    };

    const handleParticipantLeft = (participantId: string) => {
      setParticipants(prev => 
        prev.map(p => p.id === participantId ? { ...p, isOnline: false } : p)
      );

      const participant = participants.find(p => p.id === participantId);
      if (participant) {
        setActivities(prev => [{
          id: Date.now().toString(),
          type: 'leave',
          user: participant,
          description: 'left the collaboration',
          timestamp: new Date().toISOString()
        }, ...prev]);
      }
    };

    const handleCursorUpdate = (data: { userId: string; cursor: { x: number; y: number } }) => {
      setParticipants(prev => 
        prev.map(p => p.id === data.userId ? { ...p, cursor: data.cursor } : p)
      );
    };

    const handleDesignUpdate = (data: Record<string, unknown>) => {
      // Handle real-time design updates
      console.log('Design updated:', data);
    };

    const handleNewComment = (comment: Comment) => {
      setComments(prev => [comment, ...prev]);
    };

    socket.on('participant_joined', handleParticipantJoined);
    socket.on('participant_left', handleParticipantLeft);
    socket.on('cursor_update', handleCursorUpdate);
    socket.on('design_update', handleDesignUpdate);
    socket.on('new_comment', handleNewComment);

    return () => {
      socket.off('participant_joined', handleParticipantJoined);
      socket.off('participant_left', handleParticipantLeft);
      socket.off('cursor_update', handleCursorUpdate);
      socket.off('design_update', handleDesignUpdate);
      socket.off('new_comment', handleNewComment);
    };
  }, [socket, participants]);

  const handleJoinSession = async (sessionId: string) => {
    try {
      await joinSession(sessionId);
      setSession({
        id: sessionId,
        designId: 'design-123',
        participants,
        isActive: true,
        createdAt: new Date().toISOString()
      });
    } catch {
      setError('Failed to join session');
    }
  };

  const handleLeaveSession = async () => {
    try {
      await leaveSession();
      setSession(null);
    } catch {
      setError('Failed to leave session');
    }
  };

  const handleSendComment = async () => {
    if (!newComment.trim()) return;

    try {
      const comment: Comment = {
        id: Date.now().toString(),
        content: newComment,
        author: participants.find(p => p.id === userId) || participants[0],
        createdAt: new Date().toISOString()
      };

      await addComment({
        designId: session?.designId || 'design-123',
        content: newComment
      });

      setComments(prev => [comment, ...prev]);
      setNewComment('');
    } catch {
      setError('Failed to send comment');
    }
  };

  const handleShareSession = async () => {
    try {
      const shareUrl = `${window.location.origin}/collaborate/${session?.id}`;
      await navigator.clipboard.writeText(shareUrl);
      // Show success message
    } catch {
      setError('Failed to copy share link');
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Real-Time Collaboration</h1>
          <p className="text-muted-foreground">
            Collaborate on designs with your team in real-time
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? 'default' : 'destructive'} className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-2 p-4">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <span className="text-red-600">{error}</span>
          </CardContent>
        </Card>
      )}

      {!session ? (
        <Card>
          <CardHeader>
            <CardTitle>Join or Create Session</CardTitle>
            <CardDescription>
              Enter a session ID to join an existing collaboration or create a new one
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Input
                placeholder="Enter session ID"
                className="flex-1"
              />
              <Button onClick={() => handleJoinSession('session-123')}>
                Join Session
              </Button>
            </div>
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Or</p>
              <Button variant="outline" onClick={() => handleJoinSession('new-session')}>
                Create New Session
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Canvas Area */}
          <div className="lg:col-span-3 space-y-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Design Canvas</CardTitle>
                  <CardDescription>
                    Session: {session.id}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setIsVideoEnabled(!isVideoEnabled)}
                    variant={isVideoEnabled ? 'default' : 'outline'}
                    size="sm"
                  >
                    {isVideoEnabled ? <Video className="h-4 w-4" /> : <VideoOff className="h-4 w-4" />}
                  </Button>
                  <Button
                    onClick={() => setIsAudioEnabled(!isAudioEnabled)}
                    variant={isAudioEnabled ? 'default' : 'outline'}
                    size="sm"
                  >
                    {isAudioEnabled ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
                  </Button>
                  <Button onClick={handleShareSession} variant="outline" size="sm">
                    <Share2 className="h-4 w-4" />
                  </Button>
                  <Button onClick={handleLeaveSession} variant="outline" size="sm">
                    Leave
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <CollaborationCanvas
                  participants={participants}
                  onCursorUpdate={sendCursorUpdate}
                  onDesignUpdate={sendDesignUpdate}
                />
              </CardContent>
            </Card>

            {/* Comments */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Comments
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <Textarea
                      placeholder="Add a comment..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      rows={2}
                      className="flex-1"
                    />
                    <Button onClick={handleSendComment} disabled={!newComment.trim()}>
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                  <CommentsPanel comments={comments} />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Participants */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Participants ({participants.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ParticipantsList participants={participants} />
              </CardContent>
            </Card>

            {/* Activity Feed */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityFeed activities={activities} />
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
