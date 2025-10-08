import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';

interface ShareRequest {
  designId: string;
  shareType: 'public' | 'private' | 'organization';
  permissions: {
    canView: boolean;
    canEdit: boolean;
    canComment: boolean;
    canExport: boolean;
  };
  expiresAt?: string;
  password?: string;
}

interface InviteRequest {
  designId: string;
  email: string;
  role: 'viewer' | 'editor' | 'admin';
  message?: string;
}

interface CommentRequest {
  designId: string;
  content: string;
  parentCommentId?: string;
  position?: {
    x: number;
    y: number;
  };
}

interface CollaborationResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export function useCollaboration() {
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const shareDesign = async (request: ShareRequest): Promise<CollaborationResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/collaboration/api/share-design/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          design_id: request.designId,
          share_type: request.shareType,
          permissions: request.permissions,
          expires_at: request.expiresAt,
          password: request.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Share failed');
      }

      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Design share error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const inviteMember = async (request: InviteRequest): Promise<CollaborationResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/collaboration/api/invite-member/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          design_id: request.designId,
          email: request.email,
          role: request.role,
          message: request.message,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Invite failed');
      }

      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Member invite error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const updateAccess = async (designId: string, userId: string, permissions: any): Promise<CollaborationResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/collaboration/api/update-access/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          design_id: designId,
          user_id: userId,
          permissions: permissions,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Access update failed');
      }

      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Access update error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const addComment = async (request: CommentRequest): Promise<CollaborationResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/collaboration/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          design_id: request.designId,
          content: request.content,
          parent_comment_id: request.parentCommentId,
          position: request.position,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Comment failed');
      }

      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Comment error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const getComments = async (designId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/collaboration/comments/?design_id=${designId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get comments');
      }

      return data.results || [];
    } catch (error) {
      console.error('Comments fetch error:', error);
      throw error;
    }
  };

  const getCollaborators = async (designId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/collaboration/collaborations/?design_id=${designId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get collaborators');
      }

      return data.results || [];
    } catch (error) {
      console.error('Collaborators fetch error:', error);
      throw error;
    }
  };

  const getDesignVersions = async (designId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/collaboration/versions/?design_id=${designId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get versions');
      }

      return data.results || [];
    } catch (error) {
      console.error('Versions fetch error:', error);
      throw error;
    }
  };

  const getDesignActivity = async (designId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/collaboration/activities/?design_id=${designId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get activity');
      }

      return data.results || [];
    } catch (error) {
      console.error('Activity fetch error:', error);
      throw error;
    }
  };

  return {
    shareDesign,
    inviteMember,
    updateAccess,
    addComment,
    getComments,
    getCollaborators,
    getDesignVersions,
    getDesignActivity,
    isLoading,
  };
}
