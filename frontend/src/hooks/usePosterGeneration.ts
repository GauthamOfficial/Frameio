import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';

interface GenerationRequest {
  prompt: string;
  style: string;
  dimensions: string;
  colorScheme: string;
  additionalInstructions?: string;
}

interface GenerationResponse {
  success: boolean;
  jobId?: string;
  imageUrl?: string;
  metadata?: any;
  error?: string;
}

export function usePosterGeneration() {
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const generatePoster = async (request: GenerationRequest): Promise<GenerationResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/poster-generation/api/generate-poster/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          prompt: request.prompt,
          style: request.style,
          dimensions: request.dimensions,
          color_scheme: request.colorScheme,
          additional_instructions: request.additionalInstructions,
          template_id: null, // Can be used for predefined templates
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Generation failed');
      }

      return {
        success: true,
        jobId: data.job_id,
        imageUrl: data.image_url,
        metadata: data.metadata,
      };
    } catch (error) {
      console.error('Poster generation error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const getGenerationStatus = async (jobId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/poster-generation/jobs/${jobId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get status');
      }

      return data;
    } catch (error) {
      console.error('Status check error:', error);
      throw error;
    }
  };

  const getGenerationHistory = async () => {
    try {
      const token = await getToken();
      
      const response = await fetch('/api/poster-generation/history/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get history');
      }

      return data.results || [];
    } catch (error) {
      console.error('History fetch error:', error);
      throw error;
    }
  };

  const getTemplates = async () => {
    try {
      const token = await getToken();
      
      const response = await fetch('/api/poster-generation/templates/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get templates');
      }

      return data.results || [];
    } catch (error) {
      console.error('Templates fetch error:', error);
      throw error;
    }
  };

  return {
    generatePoster,
    getGenerationStatus,
    getGenerationHistory,
    getTemplates,
    isLoading,
  };
}
