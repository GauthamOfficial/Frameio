'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Loader2, Download, Share2, Edit3, Sparkles, Image as ImageIcon, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { usePosterGeneration } from '@/hooks/usePosterGeneration';
import { useExportDesign } from '@/hooks/useExportDesign';
import { useCollaboration } from '@/hooks/useCollaboration';
import { PosterEditor } from '@/components/editor/PosterEditor';
import { ExportModal } from '@/components/generate/ExportModal';
import { ShareModal } from '@/components/generate/ShareModal';

interface GenerationRequest {
  prompt: string;
  style: string;
  dimensions: string;
  colorScheme: string;
  additionalInstructions?: string;
}

interface GeneratedPoster {
  id: string;
  imageUrl: string;
  prompt: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  status: 'generating' | 'completed' | 'failed';
}

export default function AIGenerationPage() {
  useAuth();
  const [generationRequest, setGenerationRequest] = useState<GenerationRequest>({
    prompt: '',
    style: 'modern',
    dimensions: '1080x1080',
    colorScheme: 'vibrant'
  });
  
  const [generatedPosters, setGeneratedPosters] = useState<GeneratedPoster[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedPoster, setSelectedPoster] = useState<GeneratedPoster | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showEditor, setShowEditor] = useState(false);

  const { generatePoster } = usePosterGeneration();
  const { exportDesign, isLoading: isExporting } = useExportDesign();
  const { shareDesign, isLoading: isSharing } = useCollaboration();

  const handleGenerate = async () => {
    if (!generationRequest.prompt.trim()) return;

    setIsGenerating(true);
    
    try {
      const result = await generatePoster({
        prompt: generationRequest.prompt,
        style: generationRequest.style,
        dimensions: generationRequest.dimensions,
        colorScheme: generationRequest.colorScheme,
        additionalInstructions: generationRequest.additionalInstructions
      });

      if (result.success) {
        const jobId = result.jobId || Date.now().toString();
        const newPoster: GeneratedPoster = {
          id: jobId,
          imageUrl: result.imageUrl || '',
          prompt: generationRequest.prompt,
          metadata: (result.metadata && typeof result.metadata === 'object' && !Array.isArray(result.metadata)) 
            ? result.metadata as Record<string, unknown> 
            : {},
          createdAt: new Date().toISOString(),
          status: 'generating'
        };

        setGeneratedPosters(prev => [newPoster, ...prev]);
        
        // Poll for completion
        if (result.jobId) {
          pollGenerationStatus(result.jobId);
        }
      }
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const pollGenerationStatus = async (jobId: string) => {
    const maxAttempts = 30; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`/api/poster-generation/jobs/${jobId}/`);
        const data = await response.json();

        if (data.status === 'completed') {
          setGeneratedPosters(prev => 
            prev.map(poster => 
              poster.id === jobId 
                ? { ...poster, status: 'completed', imageUrl: data.result.image_url }
                : poster
            )
          );
        } else if (data.status === 'failed') {
          setGeneratedPosters(prev => 
            prev.map(poster => 
              poster.id === jobId 
                ? { ...poster, status: 'failed' }
                : poster
            )
          );
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 10000); // Poll every 10 seconds
        }
      } catch (error) {
        console.error('Error polling generation status:', error);
      }
    };

    poll();
  };

  const handleExport = async (format: 'png' | 'jpg' | 'pdf' | 'svg' | 'zip') => {
    if (!selectedPoster) return;

    try {
      const result = await exportDesign({
        designId: selectedPoster.id,
        format,
        quality: 'high'
      });

      if (result.success && result.downloadUrl) {
        // Trigger download
        const link = document.createElement('a');
        link.href = result.downloadUrl;
        link.download = `poster-${selectedPoster.id}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleExportWrapper = (format: string) => {
    const validFormats: ('png' | 'jpg' | 'pdf' | 'svg' | 'zip')[] = ['png', 'jpg', 'pdf', 'svg', 'zip'];
    if (validFormats.includes(format as 'png' | 'jpg' | 'pdf' | 'svg' | 'zip')) {
      handleExport(format as 'png' | 'jpg' | 'pdf' | 'svg' | 'zip');
    }
  };

  const handleShare = async (shareData: Record<string, unknown>) => {
    if (!selectedPoster) {
      return { success: false, error: 'No poster selected' };
    }

    try {
      const result = await shareDesign({
        designId: selectedPoster.id,
        shareType: (shareData.shareType as 'public' | 'private' | 'organization') || 'public',
        permissions: (shareData.permissions as { canView: boolean; canEdit: boolean; canComment: boolean; canExport: boolean }) || {
          canView: true,
          canEdit: false,
          canComment: false,
          canExport: false
        },
        expiresAt: shareData.expiresAt as string | undefined,
        password: shareData.password as string | undefined
      });

      if (result.success) {
        setShowShareModal(false);
      }
      
      return result;
    } catch (error) {
      console.error('Share failed:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  };

  const styleOptions = [
    { value: 'modern', label: 'Modern' },
    { value: 'vintage', label: 'Vintage' },
    { value: 'minimalist', label: 'Minimalist' },
    { value: 'artistic', label: 'Artistic' },
    { value: 'corporate', label: 'Corporate' }
  ];

  const dimensionOptions = [
    { value: '1080x1080', label: 'Square (1:1)' },
    { value: '1920x1080', label: 'Landscape (16:9)' },
    { value: '1080x1920', label: 'Portrait (9:16)' },
    { value: '1200x630', label: 'Social Media' },
    { value: '2480x3508', label: 'A4 Print' }
  ];

  const colorSchemeOptions = [
    { value: 'vibrant', label: 'Vibrant' },
    { value: 'monochrome', label: 'Monochrome' },
    { value: 'pastel', label: 'Pastel' },
    { value: 'dark', label: 'Dark' },
    { value: 'warm', label: 'Warm' },
    { value: 'cool', label: 'Cool' }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Poster Generation</h1>
          <p className="text-muted-foreground">
            Create stunning posters with AI-powered design generation
          </p>
        </div>
        <Badge variant="secondary" className="flex items-center gap-2">
          <Sparkles className="h-4 w-4" />
          AI Powered
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-5 w-5" />
              Create New Poster
            </CardTitle>
            <CardDescription>
              Describe your vision and let AI bring it to life
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">Design Prompt *</Label>
              <Textarea
                id="prompt"
                placeholder="Describe the poster you want to create... (e.g., 'A modern tech conference poster with blue gradients and clean typography')"
                value={generationRequest.prompt}
                onChange={(e) => setGenerationRequest(prev => ({ ...prev, prompt: e.target.value }))}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="style">Style</Label>
                <select
                  id="style"
                  value={generationRequest.style}
                  onChange={(e) => setGenerationRequest(prev => ({ ...prev, style: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  {styleOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dimensions">Dimensions</Label>
                <select
                  id="dimensions"
                  value={generationRequest.dimensions}
                  onChange={(e) => setGenerationRequest(prev => ({ ...prev, dimensions: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  {dimensionOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="colorScheme">Color Scheme</Label>
              <select
                id="colorScheme"
                value={generationRequest.colorScheme}
                onChange={(e) => setGenerationRequest(prev => ({ ...prev, colorScheme: e.target.value }))}
                className="w-full p-2 border rounded-md"
              >
                {colorSchemeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="additionalInstructions">Additional Instructions (Optional)</Label>
              <Textarea
                id="additionalInstructions"
                placeholder="Any specific requirements or preferences..."
                value={generationRequest.additionalInstructions || ''}
                onChange={(e) => setGenerationRequest(prev => ({ ...prev, additionalInstructions: e.target.value }))}
                rows={2}
              />
            </div>

            <Button 
              onClick={handleGenerate} 
              disabled={!generationRequest.prompt.trim() || isGenerating}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Poster
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Generated Posters */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Posters</CardTitle>
            <CardDescription>
              Your AI-generated designs will appear here
            </CardDescription>
          </CardHeader>
          <CardContent>
            {generatedPosters.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <ImageIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No posters generated yet</p>
                <p className="text-sm">Create your first poster using the form</p>
              </div>
            ) : (
              <div className="space-y-4">
                {generatedPosters.map((poster) => (
                  <div
                    key={poster.id}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedPoster?.id === poster.id ? 'ring-2 ring-primary' : 'hover:shadow-md'
                    }`}
                    onClick={() => setSelectedPoster(poster)}
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center">
                        {poster.status === 'generating' ? (
                          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        ) : poster.status === 'completed' ? (
                          /* eslint-disable-next-line @next/next/no-img-element */
                          <img
                            src={poster.imageUrl}
                            alt="Generated poster"
                            className="w-full h-full object-cover rounded-lg"
                          />
                        ) : (
                          <AlertCircle className="h-6 w-6 text-destructive" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium truncate">{poster.prompt}</h4>
                          {poster.status === 'generating' && (
                            <Badge variant="secondary">Generating</Badge>
                          )}
                          {poster.status === 'completed' && (
                            <Badge variant="default" className="bg-green-500">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Ready
                            </Badge>
                          )}
                          {poster.status === 'failed' && (
                            <Badge variant="destructive">Failed</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {new Date(poster.createdAt).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons for Selected Poster */}
      {selectedPoster && selectedPoster.status === 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle>Poster Actions</CardTitle>
            <CardDescription>
              Edit, export, or share your selected poster
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Button
                onClick={() => setShowEditor(true)}
                variant="outline"
              >
                <Edit3 className="mr-2 h-4 w-4" />
                Edit Design
              </Button>
              <Button
                onClick={() => setShowExportModal(true)}
                variant="outline"
              >
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
              <Button
                onClick={() => setShowShareModal(true)}
                variant="outline"
              >
                <Share2 className="mr-2 h-4 w-4" />
                Share
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modals */}
      {showEditor && selectedPoster && (
        <PosterEditor
          poster={selectedPoster}
          onClose={() => setShowEditor(false)}
          onSave={(editedPoster) => {
            if (editedPoster && typeof editedPoster === 'object' && 'id' in editedPoster && 'imageUrl' in editedPoster && 'prompt' in editedPoster) {
              setSelectedPoster(editedPoster as GeneratedPoster);
            }
            setShowEditor(false);
          }}
        />
      )}

      {showExportModal && selectedPoster && (
        <ExportModal
          poster={selectedPoster}
          onClose={() => setShowExportModal(false)}
          onExport={handleExportWrapper}
          isLoading={isExporting}
        />
      )}

      {showShareModal && selectedPoster && (
        <ShareModal
          poster={selectedPoster}
          onClose={() => setShowShareModal(false)}
          onShare={handleShare}
          isLoading={isSharing}
        />
      )}
    </div>
  );
}
