'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, AlertCircle, Image as ImageIcon, X } from 'lucide-react';
import Image from 'next/image';

interface PosterTemplate {
  id: string;
  name: string;
  description: string;
  prompt: string;
  thumbnail: string | null;
  thumbnail_url: string | null;
  category: string;
  subcategory: string;
  audience: string[];
  offer: string;
  is_active: boolean;
  is_featured: boolean;
}

interface TemplateFormProps {
  template?: PosterTemplate | null;
  onSuccess: () => void;
  onCancel: () => void;
}

const AUDIENCE_OPTIONS = ['Men', 'Women', 'Kids', 'Unisex'];

export default function TemplateForm({ template, onSuccess, onCancel }: TemplateFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    prompt: '',
    category: '',
    subcategory: '',
    audience: [] as string[],
    offer: '',
    is_active: true,
    is_featured: false,
  });
  const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name || '',
        description: template.description || '',
        prompt: template.prompt || '',
        category: template.category || '',
        subcategory: template.subcategory || '',
        audience: template.audience || [],
        offer: template.offer || '',
        is_active: template.is_active ?? true,
        is_featured: template.is_featured ?? false,
      });
      if (template.thumbnail_url) {
        setThumbnailPreview(template.thumbnail_url);
      }
    }
  }, [template]);

  const handleInputChange = (field: string, value: string | boolean | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAudienceToggle = (audience: string) => {
    setFormData(prev => ({
      ...prev,
      audience: prev.audience.includes(audience)
        ? prev.audience.filter(a => a !== audience)
        : [...prev.audience, audience]
    }));
  };

  const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setThumbnailFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setThumbnailPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveThumbnail = () => {
    setThumbnailFile(null);
    setThumbnailPreview(template?.thumbnail_url || null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('prompt', formData.prompt);
      formDataToSend.append('category', formData.category);
      formDataToSend.append('subcategory', formData.subcategory);
      formDataToSend.append('audience', JSON.stringify(formData.audience));
      formDataToSend.append('offer', formData.offer || 'No Offer');
      formDataToSend.append('is_active', String(formData.is_active));
      formDataToSend.append('is_featured', String(formData.is_featured));

      if (thumbnailFile) {
        formDataToSend.append('thumbnail', thumbnailFile);
      }

      const url = template
        ? `/api/admin/templates/${template.id}`
        : '/api/admin/templates';

      const method = template ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        credentials: 'include',
        body: formDataToSend,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `Failed to ${template ? 'update' : 'create'} template`);
      }

      onSuccess();
    } catch (err) {
      console.error('Error saving template:', err);
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="flex items-start gap-2 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span className="break-words">{error}</span>
        </div>
      )}

      {/* Basic Information */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            required
            placeholder="Template name"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Template description"
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="prompt">Prompt *</Label>
          <Textarea
            id="prompt"
            value={formData.prompt}
            onChange={(e) => handleInputChange('prompt', e.target.value)}
            required
            placeholder="Enter the prompt text for poster generation"
            rows={6}
            className="font-mono text-sm"
          />
          <p className="text-xs text-muted-foreground">
            This prompt will be used when users select this template
          </p>
        </div>
      </div>

      {/* Thumbnail Upload */}
      <div className="space-y-2">
        <Label>Thumbnail</Label>
        <div className="space-y-4">
          {thumbnailPreview ? (
            <div className="relative inline-block">
              <div className="aspect-[4/3] w-64 rounded-lg overflow-hidden border-2 border-dashed border-gray-300 relative">
                <Image
                  src={thumbnailPreview}
                  alt="Thumbnail preview"
                  fill
                  className="object-cover"
                  sizes="256px"
                  unoptimized
                />
              </div>
              <Button
                type="button"
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={handleRemoveThumbnail}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="aspect-[4/3] w-64 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <ImageIcon className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                <p className="text-sm text-gray-500">No thumbnail</p>
              </div>
            </div>
          )}
          <div>
            <Input
              type="file"
              accept="image/*"
              onChange={handleThumbnailChange}
              className="cursor-pointer"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Upload a thumbnail image for this template
            </p>
          </div>
        </div>
      </div>

      {/* Categorization */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <Input
            id="category"
            value={formData.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
            placeholder="e.g., Fashion, Festival, Event"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="subcategory">Subcategory</Label>
          <Input
            id="subcategory"
            value={formData.subcategory}
            onChange={(e) => handleInputChange('subcategory', e.target.value)}
            placeholder="e.g., Wedding, Casual, Formal"
          />
        </div>
      </div>

      {/* Audience */}
      <div className="space-y-2">
        <Label>Target Audience</Label>
        <div className="flex flex-wrap gap-3">
          {AUDIENCE_OPTIONS.map((audience) => (
            <div key={audience} className="flex items-center space-x-2">
              <Checkbox
                id={`audience-${audience}`}
                checked={formData.audience.includes(audience)}
                onCheckedChange={() => handleAudienceToggle(audience)}
              />
              <Label
                htmlFor={`audience-${audience}`}
                className="text-sm font-normal cursor-pointer"
              >
                {audience}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Offer */}
      <div className="space-y-2">
        <Label htmlFor="offer">Offer</Label>
        <Input
          id="offer"
          value={formData.offer}
          onChange={(e) => handleInputChange('offer', e.target.value)}
          placeholder="e.g., 20% Off, Buy 2 Get 1 Free, or 'No Offer'"
        />
      </div>

      {/* Status Flags */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="is_active"
            checked={formData.is_active}
            onCheckedChange={(checked) => handleInputChange('is_active', checked === true)}
          />
          <Label htmlFor="is_active" className="text-sm font-normal cursor-pointer">
            Active (visible to users)
          </Label>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="is_featured"
            checked={formData.is_featured}
            onCheckedChange={(checked) => handleInputChange('is_featured', checked === true)}
          />
          <Label htmlFor="is_featured" className="text-sm font-normal cursor-pointer">
            Featured (shown prominently)
          </Label>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              {template ? 'Updating...' : 'Creating...'}
            </>
          ) : (
            template ? 'Update Template' : 'Create Template'
          )}
        </Button>
      </div>
    </form>
  );
}

