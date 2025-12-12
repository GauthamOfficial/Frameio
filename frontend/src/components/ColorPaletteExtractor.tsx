"use client"

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Palette, Download, Copy, RefreshCw } from 'lucide-react';
import { useToastHelpers } from '@/components/common';

export interface ColorInfo {
  hex: string;
  rgb: [number, number, number];
  hsl: [number, number, number];
  percentage: number;
  name?: string;
}

export interface ColorPaletteExtractorProps {
  imageUrl?: string;
  onPaletteExtracted?: (palette: ColorInfo[]) => void;
  maxColors?: number;
  className?: string;
}

/**
 * Color Palette Extractor Component
 * Extracts dominant colors from images using canvas-based color analysis
 */
export default function ColorPaletteExtractor({
  imageUrl,
  onPaletteExtracted,
  maxColors = 5,
  className = '',
}: ColorPaletteExtractorProps) {
  const { showSuccess, showError } = useToastHelpers();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [palette, setPalette] = useState<ColorInfo[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [imageLoaded, setImageLoaded] = useState(false);

  // Color name mapping for common colors
  const colorNames: Record<string, string> = {
    '#FF0000': 'Red',
    '#00FF00': 'Green',
    '#0000FF': 'Blue',
    '#FFFF00': 'Yellow',
    '#FF00FF': 'Magenta',
    '#00FFFF': 'Cyan',
    '#000000': 'Black',
    '#FFFFFF': 'White',
    '#800000': 'Maroon',
    '#008000': 'Green',
    '#000080': 'Navy',
    '#808000': 'Olive',
    '#800080': 'Purple',
    '#008080': 'Teal',
    '#C0C0C0': 'Silver',
    '#808080': 'Gray',
    '#FFA500': 'Orange',
    '#FFC0CB': 'Pink',
    '#A52A2A': 'Brown',
    '#FFD700': 'Gold',
  };

  useEffect(() => {
    if (imageUrl) {
      extractColors(imageUrl);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageUrl]);

  /**
   * Extract colors from image using canvas
   */
  const extractColors = async (url: string) => {
    setIsExtracting(true);
    setImageLoaded(false);

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        setImageLoaded(true);
        const colors = extractColorsFromImage(img);
        setPalette(colors);
        onPaletteExtracted?.(colors);
        setIsExtracting(false);
      };

      img.onerror = () => {
        showError('Failed to load image for color extraction');
        setIsExtracting(false);
      };

      img.src = url;
    } catch {
      showError('Error extracting colors from image');
      setIsExtracting(false);
    }
  };

  /**
   * Extract colors from image element
   */
  const extractColorsFromImage = (img: HTMLImageElement): ColorInfo[] => {
    const canvas = canvasRef.current;
    if (!canvas) return [];

    const ctx = canvas.getContext('2d');
    if (!ctx) return [];

    // Set canvas size
    const maxSize = 200;
    const ratio = Math.min(maxSize / img.width, maxSize / img.height);
    canvas.width = img.width * ratio;
    canvas.height = img.height * ratio;

    // Draw image to canvas
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;

    // Count color frequencies
    const colorCounts: Record<string, number> = {};
    const totalPixels = pixels.length / 4;

    for (let i = 0; i < pixels.length; i += 4) {
      const r = pixels[i];
      const g = pixels[i + 1];
      const b = pixels[i + 2];
      const a = pixels[i + 3];

      // Skip transparent pixels
      if (a < 128) continue;

      // Quantize colors to reduce noise
      const quantizedR = Math.round(r / 32) * 32;
      const quantizedG = Math.round(g / 32) * 32;
      const quantizedB = Math.round(b / 32) * 32;

      const colorKey = `${quantizedR},${quantizedG},${quantizedB}`;
      colorCounts[colorKey] = (colorCounts[colorKey] || 0) + 1;
    }

    // Convert to color info objects and sort by frequency
    const colors: ColorInfo[] = Object.entries(colorCounts)
      .map(([colorKey, count]) => {
        const [r, g, b] = colorKey.split(',').map(Number);
        const hex = rgbToHex(r, g, b);
        const hsl = rgbToHsl(r, g, b);
        const percentage = (count / totalPixels) * 100;

        return {
          hex,
          rgb: [r, g, b] as [number, number, number],
          hsl,
          percentage,
          name: colorNames[hex] || getColorName(r, g, b),
        };
      })
      .sort((a, b) => b.percentage - a.percentage)
      .slice(0, maxColors);

    return colors;
  };

  /**
   * Convert RGB to hex
   */
  const rgbToHex = (r: number, g: number, b: number): string => {
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
  };

  /**
   * Convert RGB to HSL
   */
  const rgbToHsl = (r: number, g: number, b: number): [number, number, number] => {
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h = 0;
    let s = 0;
    const l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

      switch (max) {
        case r:
          h = (g - b) / d + (g < b ? 6 : 0);
          break;
        case g:
          h = (b - r) / d + 2;
          break;
        case b:
          h = (r - g) / d + 4;
          break;
      }
      h /= 6;
    }

    return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
  };

  /**
   * Get color name based on RGB values
   */
  const getColorName = (r: number, g: number, b: number): string => {
    // Simple color name detection based on dominant channel
    if (r > g && r > b) {
      if (r > 200) return 'Light Red';
      if (r > 100) return 'Red';
      return 'Dark Red';
    }
    if (g > r && g > b) {
      if (g > 200) return 'Light Green';
      if (g > 100) return 'Green';
      return 'Dark Green';
    }
    if (b > r && b > g) {
      if (b > 200) return 'Light Blue';
      if (b > 100) return 'Blue';
      return 'Dark Blue';
    }
    if (r === g && g === b) {
      if (r > 200) return 'Light Gray';
      if (r > 100) return 'Gray';
      return 'Dark Gray';
    }
    return 'Mixed Color';
  };

  /**
   * Copy color to clipboard
   */
  const copyColor = async (color: string) => {
    try {
      // Try modern Clipboard API first (works on HTTPS)
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(color);
        showSuccess(`Copied ${color} to clipboard`);
        return;
      }
      
      // Fallback for HTTP or when Clipboard API is not available
      const textArea = document.createElement('textarea');
      textArea.value = color;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          showSuccess(`Copied ${color} to clipboard`);
        } else {
          throw new Error('execCommand failed');
        }
      } finally {
        document.body.removeChild(textArea);
      }
    } catch {
      showError('Failed to copy color');
    }
  };

  /**
   * Download palette as JSON
   */
  const downloadPalette = () => {
    const dataStr = JSON.stringify(palette, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `color-palette-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showSuccess('Palette downloaded successfully');
  };

  /**
   * Refresh color extraction
   */
  const refreshPalette = () => {
    if (imageUrl) {
      extractColors(imageUrl);
    }
  };

  return (
    <Card className={`textile-hover textile-shadow ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Color Palette
          </CardTitle>
          <div className="flex gap-2">
            {palette.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadPalette}
                  title="Download palette"
                >
                  <Download className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={refreshPalette}
                  disabled={isExtracting}
                  title="Refresh palette"
                >
                  <RefreshCw className={`h-4 w-4 ${isExtracting ? 'animate-spin' : ''}`} />
                </Button>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Hidden canvas for color extraction */}
        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />

        {isExtracting ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
              <p className="text-sm text-muted-foreground">Extracting colors...</p>
            </div>
          </div>
        ) : palette.length > 0 ? (
          <div className="space-y-4">
            {/* Color swatches */}
            <div className="grid grid-cols-5 gap-2">
              {palette.map((color, index) => (
                <div
                  key={index}
                  className="group relative"
                >
                  <div
                    className="w-full h-16 rounded-lg border-2 border-border cursor-pointer transition-transform hover:scale-105"
                    style={{ backgroundColor: color.hex }}
                    onClick={() => copyColor(color.hex)}
                    title={`${color.hex} - ${color.name} (${color.percentage.toFixed(1)}%)`}
                  />
                  
                  {/* Color info overlay */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                    <div className="text-center text-white text-xs">
                      <div className="font-mono">{color.hex}</div>
                      <div className="text-xs opacity-80">{color.percentage.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Color details */}
            <div className="space-y-2">
              {palette.map((color, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-muted rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-6 h-6 rounded border border-border"
                      style={{ backgroundColor: color.hex }}
                    />
                    <div>
                      <div className="font-mono text-sm font-medium">{color.hex}</div>
                      <div className="text-xs text-muted-foreground">
                        {color.name} • {color.percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyColor(color.hex)}
                    title="Copy color"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        ) : imageUrl ? (
          <div className="text-center py-8">
            <Palette className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">No colors extracted yet</p>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshPalette}
              className="mt-2"
            >
              Extract Colors
            </Button>
          </div>
        ) : (
          <div className="text-center py-8">
            <Palette className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Upload an image to extract colors</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
