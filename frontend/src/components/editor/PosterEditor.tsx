'use client';

import dynamic from 'next/dynamic';

const PosterEditorInternal = dynamic(() => import('./PosterEditorInternal'), { 
  ssr: false 
});
interface PosterEditorProps {
  poster: {
    id: string;
    imageUrl: string;
    prompt: string;
    metadata: any;
  };
  onClose: () => void;
  onSave: (editedPoster: any) => void;
}

export function PosterEditor(props: PosterEditorProps) {
  return <PosterEditorInternal {...props} />;
}
