"use client"

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Eye, Download, Heart, Star } from 'lucide-react';
import { useToastHelpers } from '@/components/common';
import { ColorInfo } from './ColorPaletteExtractor';

export interface Template {
  id: number;
  name: string;
  description: string;
  tags: string[];
  category: string;
  style: string;
  colorScheme: string[];
  previewUrl: string;
  downloadUrl: string;
  rating: number;
  usageCount: number;
  isPremium: boolean;
  metadata: {
    created_at: string;
    updated_at: string;
    author: string;
    version: string;
  };
}

export interface TemplateRecommenderProps {
  theme?: string;
  colorPalette?: ColorInfo[];
  style?: string;
  onTemplateSelect?: (template: Template) => void;
  className?: string;
}

// Mock template data (until backend ML model is available)
const MOCK_TEMPLATES: Template[] = [
  {
    id: 1,
    name: "Minimal Textile Poster",
    description: "Clean and elegant design perfect for modern textile collections",
    tags: ["minimal", "cotton", "elegant", "modern", "clean"],
    category: "poster",
    style: "minimalist",
    colorScheme: ["#FFFFFF", "#F5F5F5", "#E0E0E0", "#9E9E9E", "#424242"],
    previewUrl: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=500&fit=crop",
    downloadUrl: "/templates/minimal-textile-poster.zip",
    rating: 4.8,
    usageCount: 1250,
    isPremium: false,
    metadata: {
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-20T15:30:00Z",
      author: "Frameio Design Team",
      version: "1.2.0",
    },
  },
  {
    id: 2,
    name: "Festive Saree Banner",
    description: "Vibrant and traditional design for festive saree collections",
    tags: ["festive", "saree", "traditional", "red", "gold", "luxury"],
    category: "banner",
    style: "traditional",
    colorScheme: ["#DC2626", "#F59E0B", "#FEF3C7", "#7C2D12", "#000000"],
    previewUrl: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=500&fit=crop",
    downloadUrl: "/templates/festive-saree-banner.zip",
    rating: 4.9,
    usageCount: 2100,
    isPremium: false,
    metadata: {
      created_at: "2024-01-10T09:00:00Z",
      updated_at: "2024-01-18T12:00:00Z",
      author: "Frameio Design Team",
      version: "2.1.0",
    },
  },
  {
    id: 3,
    name: "Casual Wear Catalog",
    description: "Modern and trendy design for casual wear collections",
    tags: ["casual", "denim", "youth", "modern", "blue", "comfortable"],
    category: "catalog",
    style: "modern",
    colorScheme: ["#3B82F6", "#1E40AF", "#93C5FD", "#F3F4F6", "#FFFFFF"],
    previewUrl: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=500&fit=crop",
    downloadUrl: "/templates/casual-wear-catalog.zip",
    rating: 4.7,
    usageCount: 980,
    isPremium: false,
    metadata: {
      created_at: "2024-01-12T14:00:00Z",
      updated_at: "2024-01-19T11:00:00Z",
      author: "Frameio Design Team",
      version: "1.5.0",
    },
  },
  {
    id: 4,
    name: "Luxury Silk Collection",
    description: "Premium design showcasing luxury silk products",
    tags: ["luxury", "silk", "premium", "elegant", "gold", "sophisticated"],
    category: "poster",
    style: "elegant",
    colorScheme: ["#F59E0B", "#FEF3C7", "#7C2D12", "#000000", "#FFFFFF"],
    previewUrl: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=500&fit=crop",
    downloadUrl: "/templates/luxury-silk-collection.zip",
    rating: 4.9,
    usageCount: 750,
    isPremium: true,
    metadata: {
      created_at: "2024-01-08T16:00:00Z",
      updated_at: "2024-01-17T13:00:00Z",
      author: "Frameio Design Team",
      version: "1.8.0",
    },
  },
  {
    id: 5,
    name: "Bohemian Textile Mix",
    description: "Artistic and free-spirited design for bohemian collections",
    tags: ["bohemian", "artistic", "colorful", "creative", "eclectic"],
    category: "poster",
    style: "bohemian",
    colorScheme: ["#EC4899", "#8B5CF6", "#06B6D4", "#F59E0B", "#10B981"],
    previewUrl: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=500&fit=crop",
    downloadUrl: "/templates/bohemian-textile-mix.zip",
    rating: 4.6,
    usageCount: 650,
    isPremium: false,
    metadata: {
      created_at: "2024-01-14T11:00:00Z",
      updated_at: "2024-01-21T09:00:00Z",
      author: "Frameio Design Team",
      version: "1.3.0",
    },
  },
  {
    id: 6,
    name: "Wedding Collection Showcase",
    description: "Romantic and elegant design for wedding textile collections",
    tags: ["wedding", "romantic", "elegant", "white", "gold", "ceremonial"],
    category: "showcase",
    style: "elegant",
    colorScheme: ["#FFFFFF", "#FEF3C7", "#F59E0B", "#F3F4F6", "#9CA3AF"],
    previewUrl: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=500&fit=crop",
    downloadUrl: "/templates/wedding-collection-showcase.zip",
    rating: 4.8,
    usageCount: 1100,
    isPremium: true,
    metadata: {
      created_at: "2024-01-11T13:00:00Z",
      updated_at: "2024-01-20T10:00:00Z",
      author: "Frameio Design Team",
      version: "2.0.0",
    },
  },
];

/**
 * Template Recommender Component
 * Recommends templates based on theme, colors, and style preferences
 */
export default function TemplateRecommender({
  theme = '',
  colorPalette = [],
  style = '',
  onTemplateSelect,
  className = '',
}: TemplateRecommenderProps) {
  const { showSuccess, showError } = useToastHelpers();
  const [recommendedTemplates, setRecommendedTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  useEffect(() => {
    if (theme || colorPalette.length > 0 || style) {
      generateRecommendations();
    }
  }, [theme, colorPalette, style]);

  /**
   * Generate template recommendations based on input parameters
   */
  const generateRecommendations = async () => {
    setIsLoading(true);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const recommendations = getRecommendedTemplates(theme, colorPalette, style);
      setRecommendedTemplates(recommendations);
    } catch (error) {
      showError('Failed to generate recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get recommended templates based on theme, palette, and style
   */
  const getRecommendedTemplates = (
    theme: string,
    palette: ColorInfo[],
    style: string
  ): Template[] => {
    let scoredTemplates = MOCK_TEMPLATES.map(template => ({
      ...template,
      score: calculateTemplateScore(template, theme, palette, style),
    }));

    // Sort by score (highest first) and take top 3
    return scoredTemplates
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(({ score, ...template }) => template);
  };

  /**
   * Calculate template relevance score
   */
  const calculateTemplateScore = (
    template: Template,
    theme: string,
    palette: ColorInfo[],
    style: string
  ): number => {
    let score = 0;

    // Style matching (40% weight)
    if (style && template.style.toLowerCase() === style.toLowerCase()) {
      score += 40;
    }

    // Theme/tag matching (30% weight)
    const themeWords = theme.toLowerCase().split(' ');
    const matchingTags = template.tags.filter(tag =>
      themeWords.some(word => tag.toLowerCase().includes(word))
    );
    score += (matchingTags.length / template.tags.length) * 30;

    // Color matching (20% weight)
    if (palette.length > 0) {
      const templateColors = template.colorScheme.map(color => color.toLowerCase());
      const matchingColors = palette.filter(color =>
        templateColors.some(templateColor =>
          isColorSimilar(color.hex.toLowerCase(), templateColor)
        )
      );
      score += (matchingColors.length / palette.length) * 20;
    }

    // Popularity bonus (10% weight)
    score += Math.min(template.rating * 2, 10);

    return score;
  };

  /**
   * Check if two colors are similar
   */
  const isColorSimilar = (color1: string, color2: string): boolean => {
    // Simple color similarity check
    const hex1 = color1.replace('#', '');
    const hex2 = color2.replace('#', '');
    
    const r1 = parseInt(hex1.substr(0, 2), 16);
    const g1 = parseInt(hex1.substr(2, 2), 16);
    const b1 = parseInt(hex1.substr(4, 2), 16);
    
    const r2 = parseInt(hex2.substr(0, 2), 16);
    const g2 = parseInt(hex2.substr(2, 2), 16);
    const b2 = parseInt(hex2.substr(4, 2), 16);
    
    const distance = Math.sqrt(
      Math.pow(r2 - r1, 2) + Math.pow(g2 - g1, 2) + Math.pow(b2 - b1, 2)
    );
    
    return distance < 100; // Threshold for color similarity
  };

  /**
   * Handle template selection
   */
  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    onTemplateSelect?.(template);
    showSuccess(`Selected template: ${template.name}`);
  };

  /**
   * Handle template preview
   */
  const handleTemplatePreview = (template: Template) => {
    // Open template preview in new window
    window.open(template.previewUrl, '_blank');
  };

  /**
   * Handle template download
   */
  const handleTemplateDownload = (template: Template) => {
    if (template.isPremium) {
      showError('Premium templates require subscription');
      return;
    }
    
    // Simulate download
    showSuccess(`Downloading ${template.name}...`);
  };

  return (
    <Card className={`textile-hover textile-shadow ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          Suggested Templates
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <Sparkles className="h-8 w-8 animate-pulse mx-auto mb-2 text-primary" />
              <p className="text-sm text-muted-foreground">Finding perfect templates...</p>
            </div>
          </div>
        ) : recommendedTemplates.length > 0 ? (
          <div className="space-y-4">
            {recommendedTemplates.map((template) => (
              <div
                key={template.id}
                className={`border rounded-lg p-4 transition-all hover:shadow-md ${
                  selectedTemplate?.id === template.id
                    ? 'border-primary bg-primary/5'
                    : 'border-border'
                }`}
              >
                <div className="flex gap-4">
                  {/* Template Preview */}
                  <div className="w-20 h-24 bg-muted rounded-lg overflow-hidden flex-shrink-0">
                    <img
                      src={template.previewUrl}
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Template Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-sm">{template.name}</h3>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {template.description}
                        </p>
                      </div>
                      {template.isPremium && (
                        <Badge variant="secondary" className="text-xs">
                          Premium
                        </Badge>
                      )}
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {template.tags.slice(0, 4).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-current" />
                        {template.rating}
                      </div>
                      <div>{template.usageCount} uses</div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTemplateSelect(template)}
                        className="flex-1"
                      >
                        Select
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleTemplatePreview(template)}
                        title="Preview"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleTemplateDownload(template)}
                        title="Download"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground mb-2">No templates to recommend yet</p>
            <p className="text-sm text-muted-foreground">
              Add a theme, upload images, or select a style to get personalized recommendations
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
