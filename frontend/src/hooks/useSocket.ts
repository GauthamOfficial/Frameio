'use client';

import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '@clerk/nextjs';

interface SocketEventHandlers {
  [key: string]: (...args: unknown[]) => void;
}

export function useSocket() {
  const { getToken } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventHandlers = useRef<SocketEventHandlers>({});

  useEffect(() => {
    const initializeSocket = async () => {
      try {
        const token = await getToken();
        
        // Use API_BASE_URL for socket connection (socket.io typically uses same base as API)
        const { API_BASE_URL } = await import('@/utils/api');
        const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL || API_BASE_URL;
        const newSocket = io(socketUrl, {
          auth: {
            token: token
          },
          transports: ['websocket', 'polling']
        });

        newSocket.on('connect', () => {
          console.log('Socket connected:', newSocket.id);
          setIsConnected(true);
          setError(null);
        });

        newSocket.on('disconnect', (reason) => {
          console.log('Socket disconnected:', reason);
          setIsConnected(false);
        });

        newSocket.on('connect_error', (err) => {
          console.error('Socket connection error:', err);
          setError('Failed to connect to collaboration server');
          setIsConnected(false);
        });

        // Register existing event handlers
        Object.entries(eventHandlers.current).forEach(([event, handler]) => {
          newSocket.on(event, handler);
        });

        setSocket(newSocket);

        return () => {
          newSocket.close();
        };
      } catch (error) {
        console.error('Socket initialization error:', error);
        setError('Failed to initialize socket connection');
      }
    };

    initializeSocket();
  }, [getToken]);

  const on = (event: string, handler: (...args: unknown[]) => void) => {
    eventHandlers.current[event] = handler;
    if (socket) {
      socket.on(event, handler);
    }
  };

  const off = (event: string, handler?: (...args: unknown[]) => void) => {
    if (handler) {
      delete eventHandlers.current[event];
    }
    if (socket) {
      socket.off(event, handler);
    }
  };

  const emit = (event: string, data?: unknown) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    } else {
      console.warn('Socket not connected, cannot emit event:', event);
    }
  };

  const joinSession = async (sessionId: string) => {
    return new Promise((resolve, reject) => {
      if (!socket) {
        reject(new Error('Socket not initialized'));
        return;
      }

      const timeout = setTimeout(() => {
        reject(new Error('Join session timeout'));
      }, 5000);

      socket.emit('join_session', { sessionId }, (response: { success?: boolean; error?: string }) => {
        clearTimeout(timeout);
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error || 'Failed to join session'));
        }
      });
    });
  };

  const leaveSession = async () => {
    return new Promise((resolve, reject) => {
      if (!socket) {
        reject(new Error('Socket not initialized'));
        return;
      }

      socket.emit('leave_session', {}, (response: { success?: boolean; error?: string }) => {
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error || 'Failed to leave session'));
        }
      });
    });
  };

  const sendMessage = (message: string, type: 'text' | 'system' = 'text') => {
    emit('send_message', { message, type });
  };

  const sendCursorUpdate = (cursor: { x: number; y: number }) => {
    emit('cursor_update', { cursor });
  };

  const sendDesignUpdate = (update: unknown) => {
    emit('design_update', update);
  };

  const sendComment = (comment: unknown) => {
    emit('new_comment', comment);
  };

  const requestDesignSync = () => {
    emit('request_design_sync');
  };

  const sendDesignSync = (designData: unknown) => {
    emit('design_sync', designData);
  };

  const sendParticipantUpdate = (update: unknown) => {
    emit('participant_update', update);
  };

  const sendActivity = (activity: unknown) => {
    emit('activity', activity);
  };

  return {
    socket,
    isConnected,
    error,
    on,
    off,
    emit,
    joinSession,
    leaveSession,
    sendMessage,
    sendCursorUpdate,
    sendDesignUpdate,
    sendComment,
    requestDesignSync,
    sendDesignSync,
    sendParticipantUpdate,
    sendActivity
  };
}
