'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Reply, 
  MoreVertical, 
  ThumbsUp,
  ThumbsDown,
  Flag
} from 'lucide-react';

interface Participant {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'editor' | 'viewer';
  isOnline: boolean;
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
  likes?: number;
  isLiked?: boolean;
}

interface CommentsPanelProps {
  comments: Comment[];
}

export function CommentsPanel({ comments }: CommentsPanelProps) {
  const [expandedReplies, setExpandedReplies] = useState<Set<string>>(new Set());
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyText, setReplyText] = useState('');

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const toggleReplies = (commentId: string) => {
    setExpandedReplies(prev => {
      const newSet = new Set(prev);
      if (newSet.has(commentId)) {
        newSet.delete(commentId);
      } else {
        newSet.add(commentId);
      }
      return newSet;
    });
  };

  const handleReply = (commentId: string) => {
    setReplyingTo(commentId);
    setReplyText('');
  };

  const handleSubmitReply = () => {
    if (!replyText.trim() || !replyingTo) return;
    
    // Here you would typically send the reply to the backend
    console.log('Submitting reply:', { commentId: replyingTo, content: replyText });
    
    setReplyingTo(null);
    setReplyText('');
  };

  const handleLike = (commentId: string) => {
    // Here you would typically send the like to the backend
    console.log('Liking comment:', commentId);
  };

  const CommentItem = ({ comment, isReply = false }: { comment: Comment; isReply?: boolean }) => (
    <div className={`space-y-3 ${isReply ? 'ml-8 border-l-2 border-gray-200 pl-4' : ''}`}>
      <div className="flex gap-3">
        <Avatar className="h-8 w-8">
          <AvatarImage src={comment.author.avatar} />
          <AvatarFallback className="text-xs">
            {getInitials(comment.author.name)}
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">{comment.author.name}</span>
            <Badge variant="outline" className="text-xs">
              {comment.author.role}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {formatTimeAgo(comment.createdAt)}
            </span>
          </div>
          
          <p className="text-sm text-gray-700">{comment.content}</p>
          
          {comment.position && (
            <div className="text-xs text-muted-foreground">
              Position: ({comment.position.x}, {comment.position.y})
            </div>
          )}
          
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleLike(comment.id)}
              className="h-6 px-2 text-xs"
            >
              <ThumbsUp className="h-3 w-3 mr-1" />
              {comment.likes || 0}
            </Button>
            
            {!isReply && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleReply(comment.id)}
                className="h-6 px-2 text-xs"
              >
                <Reply className="h-3 w-3 mr-1" />
                Reply
              </Button>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs"
            >
              <MoreVertical className="h-3 w-3" />
            </Button>
          </div>
          
          {/* Reply Form */}
          {replyingTo === comment.id && (
            <div className="space-y-2">
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Write a reply..."
                className="w-full p-2 border rounded-md text-sm resize-none"
                rows={2}
              />
              <div className="flex gap-2">
                <Button
                  onClick={handleSubmitReply}
                  size="sm"
                  disabled={!replyText.trim()}
                >
                  Reply
                </Button>
                <Button
                  onClick={() => setReplyingTo(null)}
                  variant="outline"
                  size="sm"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="space-y-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleReplies(comment.id)}
            className="h-6 px-2 text-xs text-muted-foreground"
          >
            {expandedReplies.has(comment.id) ? 'Hide' : 'Show'} {comment.replies.length} replies
          </Button>
          
          {expandedReplies.has(comment.id) && (
            <div className="space-y-3">
              {comment.replies.map((reply) => (
                <CommentItem key={reply.id} comment={reply} isReply />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  if (comments.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No comments yet</p>
        <p className="text-sm">Start the conversation!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-96 overflow-y-auto">
      {comments.map((comment) => (
        <CommentItem key={comment.id} comment={comment} />
      ))}
    </div>
  );
}
