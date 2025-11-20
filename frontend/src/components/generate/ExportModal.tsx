'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Download, 
  FileImage, 
  FileText, 
  Archive, 
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface ExportModalProps {
  poster: {
    id: string;
    imageUrl: string;
    prompt: string;
  };
  onClose: () => void;
  onExport: (format: string) => void;
  isLoading: boolean;
}

interface ExportFormat {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  recommended: boolean;
}

const exportFormats: ExportFormat[] = [
  {
    id: 'png',
    name: 'PNG',
    description: 'High quality with transparency support',
    icon: <FileImage className="h-5 w-5" />,
    recommended: true
  },
  {
    id: 'jpg',
    name: 'JPEG',
    description: 'Smaller file size, good for photos',
    icon: <FileImage className="h-5 w-5" />,
    recommended: false
  },
  {
    id: 'pdf',
    name: 'PDF',
    description: 'Vector format, perfect for printing',
    icon: <FileText className="h-5 w-5" />,
    recommended: true
  },
  {
    id: 'svg',
    name: 'SVG',
    description: 'Scalable vector graphics',
    icon: <FileText className="h-5 w-5" />,
    recommended: false
  },
  {
    id: 'zip',
    name: 'ZIP',
    description: 'Multiple formats in one package',
    icon: <Archive className="h-5 w-5" />,
    recommended: false
  }
];

export function ExportModal({ poster, onClose, onExport, isLoading }: ExportModalProps) {
  const [selectedFormat, setSelectedFormat] = useState('png');
  const [customDimensions, setCustomDimensions] = useState({
    width: 1080,
    height: 1080
  });
  const [quality, setQuality] = useState('high');
  const [includeMetadata, setIncludeMetadata] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'exporting' | 'success' | 'error'>('idle');

  const handleExport = async () => {
    setExportStatus('exporting');
    try {
      await onExport(selectedFormat);
      setExportStatus('success');
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      setExportStatus('error');
    }
  };

  const qualityOptions = [
    { value: 'low', label: 'Low (Fast)' },
    { value: 'medium', label: 'Medium (Balanced)' },
    { value: 'high', label: 'High (Best Quality)' }
  ];

  const dimensionPresets = [
    { name: 'Square', width: 1080, height: 1080 },
    { name: 'Instagram Post', width: 1080, height: 1080 },
    { name: 'Instagram Story', width: 1080, height: 1920 },
    { name: 'Facebook Post', width: 1200, height: 630 },
    { name: 'Twitter Header', width: 1500, height: 500 },
    { name: 'LinkedIn Post', width: 1200, height: 627 },
    { name: 'A4 Print', width: 2480, height: 3508 },
    { name: 'Custom', width: 0, height: 0 }
  ];

  const handlePresetSelect = (preset: typeof dimensionPresets[0]) => {
    if (preset.name === 'Custom') return;
    setCustomDimensions({ width: preset.width, height: preset.height });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Design
          </CardTitle>
          <CardDescription>
            Choose your preferred format and settings for downloading
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Format Selection */}
          <div className="space-y-3">
            <Label>Export Format</Label>
            <div className="grid grid-cols-1 gap-3">
              {exportFormats.map((format) => (
                <div
                  key={format.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedFormat === format.id 
                      ? 'ring-2 ring-primary border-primary' 
                      : 'hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedFormat(format.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {format.icon}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{format.name}</span>
                          {format.recommended && (
                            <Badge variant="secondary" className="text-xs">
                              Recommended
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {format.description}
                        </p>
                      </div>
                    </div>
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      selectedFormat === format.id 
                        ? 'border-primary bg-primary' 
                        : 'border-gray-300'
                    }`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dimensions */}
          <div className="space-y-3">
            <Label>Dimensions</Label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm">Width (px)</Label>
                <Input
                  type="number"
                  value={customDimensions.width}
                  onChange={(e) => setCustomDimensions(prev => ({ 
                    ...prev, 
                    width: Number(e.target.value) 
                  }))}
                />
              </div>
              <div>
                <Label className="text-sm">Height (px)</Label>
                <Input
                  type="number"
                  value={customDimensions.height}
                  onChange={(e) => setCustomDimensions(prev => ({ 
                    ...prev, 
                    height: Number(e.target.value) 
                  }))}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm">Quick Presets</Label>
              <div className="flex flex-wrap gap-2">
                {dimensionPresets.map((preset) => (
                  <Button
                    key={preset.name}
                    variant="outline"
                    size="sm"
                    onClick={() => handlePresetSelect(preset)}
                    className="text-xs"
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Quality */}
          <div className="space-y-3">
            <Label>Quality</Label>
            <div className="grid grid-cols-3 gap-2">
              {qualityOptions.map((option) => (
                <Button
                  key={option.value}
                  variant={quality === option.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setQuality(option.value)}
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <Label>Export Options</Label>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="includeMetadata"
                checked={includeMetadata}
                onChange={(e) => setIncludeMetadata(e.target.checked)}
                className="rounded border-gray-300"
              />
              <Label htmlFor="includeMetadata" className="text-sm">
                Include metadata (prompt, creation date, etc.)
              </Label>
            </div>
          </div>

          {/* Status */}
          {exportStatus === 'exporting' && (
            <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span className="text-sm text-blue-600">Exporting your design...</span>
            </div>
          )}

          {exportStatus === 'success' && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600">Export completed successfully!</span>
            </div>
          )}

          {exportStatus === 'error' && (
            <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <span className="text-sm text-red-600">Export failed. Please try again.</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleExport}
              disabled={isLoading || exportStatus === 'exporting'}
              className="flex-1"
            >
              {exportStatus === 'exporting' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Export {selectedFormat.toUpperCase()}
                </>
              )}
            </Button>
            <Button onClick={onClose} variant="outline">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
