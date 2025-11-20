import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';

interface ExportRequest {
  designId: string;
  format: 'png' | 'jpg' | 'pdf' | 'svg' | 'zip';
  quality: 'low' | 'medium' | 'high';
  customDimensions?: {
    width: number;
    height: number;
  };
  includeMetadata?: boolean;
}

interface ExportResponse {
  success: boolean;
  downloadUrl?: string;
  jobId?: string;
  error?: string;
}

export function useExportDesign() {
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const exportDesign = async (request: ExportRequest): Promise<ExportResponse> => {
    setIsLoading(true);
    
    try {
      const token = await getToken();
      
      const response = await fetch('/api/design-export/api/export-designs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          design_id: request.designId,
          export_format: request.format,
          quality: request.quality,
          custom_dimensions: request.customDimensions,
          include_metadata: request.includeMetadata || false,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Export failed');
      }

      return {
        success: true,
        downloadUrl: data.download_url,
        jobId: data.job_id,
      };
    } catch (error) {
      console.error('Design export error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    } finally {
      setIsLoading(false);
    }
  };

  const getExportStatus = async (jobId: string) => {
    try {
      const token = await getToken();
      
      const response = await fetch(`/api/design-export/jobs/${jobId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get export status');
      }

      return data;
    } catch (error) {
      console.error('Export status check error:', error);
      throw error;
    }
  };

  const getExportHistory = async () => {
    try {
      const token = await getToken();
      
      const response = await fetch('/api/design-export/history/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get export history');
      }

      return data.results || [];
    } catch (error) {
      console.error('Export history fetch error:', error);
      throw error;
    }
  };

  const getExportTemplates = async () => {
    try {
      const token = await getToken();
      
      const response = await fetch('/api/design-export/templates/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get export templates');
      }

      return data.results || [];
    } catch (error) {
      console.error('Export templates fetch error:', error);
      throw error;
    }
  };

  const downloadFile = async (downloadUrl: string, filename: string) => {
    try {
      const response = await fetch(downloadUrl);
      const blob = await response.blob();
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Download error:', error);
      throw error;
    }
  };

  return {
    exportDesign,
    getExportStatus,
    getExportHistory,
    getExportTemplates,
    downloadFile,
    isLoading,
  };
}
