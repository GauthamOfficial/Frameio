'use client';

<<<<<<< HEAD
import dynamic from 'next/dynamic';

const FabricCanvas = dynamic(() => import('./FabricCanvasInternal'), { 
  ssr: false 
});
=======
import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { User } from 'lucide-react';
>>>>>>> build-fix

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
  onDesignUpdate: (update: unknown) => void;
}

<<<<<<< HEAD
export function CollaborationCanvas(props: CollaborationCanvasProps) {
  return <FabricCanvas {...props} />;
=======
export function CollaborationCanvas({ 
  participants, 
  onCursorUpdate, 
  onDesignUpdate 
}: CollaborationCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [canvas, setCanvas] = useState<unknown | null>(null); // fabric.Canvas - using unknown to avoid SSR issues
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Import fabric.js only on client side
    import('fabric').then((fabricModule) => {
      const { fabric } = fabricModule;
      
      const fabricCanvas = new fabric.Canvas(canvasRef.current!, {
        width: 800,
        height: 600,
        backgroundColor: '#ffffff'
      });

      // Add some sample content
      const sampleText = new fabric.Text('Collaborative Design', {
      left: 100,
      top: 100,
      fontSize: 32,
      fill: '#333333',
      fontFamily: 'Arial'
    });

    const sampleRect = new fabric.Rect({
      left: 200,
      top: 200,
      width: 100,
      height: 100,
      fill: '#4F46E5',
      selectable: true,
      evented: true
    });

    fabricCanvas.add(sampleText, sampleRect);

    // Event listeners for real-time collaboration
    fabricCanvas.on('mouse:move', (e) => {
      if (e.pointer) {
        onCursorUpdate({ x: e.pointer.x, y: e.pointer.y });
      }
    });

    fabricCanvas.on('object:added', (e) => {
      onDesignUpdate({
        type: 'object_added',
        object: e.target?.toObject()
      });
    });

    fabricCanvas.on('object:modified', (e) => {
      onDesignUpdate({
        type: 'object_modified',
        object: e.target?.toObject()
      });
    });

    fabricCanvas.on('object:removed', (e) => {
      onDesignUpdate({
        type: 'object_removed',
        object: e.target?.toObject()
      });
    });

      setCanvas(fabricCanvas);
      setIsLoading(false);

      return () => {
        fabricCanvas.dispose();
      };
    }).catch((error) => {
      console.error('Failed to load fabric.js:', error);
      setIsLoading(false);
    });
  }, [onCursorUpdate, onDesignUpdate]);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-500';
      case 'editor': return 'bg-blue-500';
      case 'viewer': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>Loading canvas...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="relative">
      <Card>
        <CardContent className="p-0">
          <div className="relative">
            <canvas ref={canvasRef} className="border border-gray-200 rounded-lg" />
            
            {/* Participant Cursors */}
            {participants
              .filter(p => p.isOnline && p.cursor && p.id !== 'current-user')
              .map((participant) => (
                <div
                  key={participant.id}
                  className="absolute pointer-events-none z-10"
                  style={{
                    left: participant.cursor!.x,
                    top: participant.cursor!.y,
                    transform: 'translate(-2px, -2px)'
                  }}
                >
                  <div className="flex items-center gap-1">
                    <div className={`w-4 h-4 rounded-full ${getRoleColor(participant.role)}`} />
                    <div className="bg-black text-white text-xs px-2 py-1 rounded shadow-lg">
                      {participant.name}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Participant Status */}
      <div className="mt-4 flex flex-wrap gap-2">
        {participants.map((participant) => (
          <Badge
            key={participant.id}
            variant={participant.isOnline ? 'default' : 'secondary'}
            className="flex items-center gap-1"
          >
            <div className={`w-2 h-2 rounded-full ${
              participant.isOnline ? 'bg-green-500' : 'bg-gray-400'
            }`} />
            <User className="h-3 w-3" />
            {participant.name}
            <span className="text-xs opacity-75">({participant.role})</span>
          </Badge>
        ))}
      </div>
    </div>
  );
>>>>>>> build-fix
}
