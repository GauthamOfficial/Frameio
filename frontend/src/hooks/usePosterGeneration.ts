import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

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
  metadata?: unknown;
  error?: string;
}

export function usePosterGeneration() {
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const generatePoster = async (request: GenerationRequest): Promise<GenerationResponse> => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/test/two-step/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          custom_text: request.prompt,
          style: request.style,
          fabric_type: 'silk', // Default fabric type
          festival: 'general', // Default festival
          price_range: '₹2999', // Default price range
          offer_details: 'Special offer available',
          generation_type: 'poster',
          color_scheme: request.colorScheme,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Generation failed');
      }

      return {
        success: true,
        jobId: data.metadata?.generated_at || Date.now().toString(),
        imageUrl: data.poster_url,
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
