'use client';

import dynamic from 'next/dynamic';

const FabricCanvas = dynamic(() => import('./FabricCanvasInternal'), { 
  ssr: false 
});

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

interface CollaborationCanvasProps {
  participants: Participant[];
  onCursorUpdate: (cursor: { x: number; y: number }) => void;
  onDesignUpdate: (update: any) => void;
}

export function CollaborationCanvas(props: CollaborationCanvasProps) {
  return <FabricCanvas {...props} />;
}
