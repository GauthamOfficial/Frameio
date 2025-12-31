'use client';

import { useState, useEffect, useMemo } from 'react';
import { useAdminAuth } from '@/contexts/admin-auth-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  FileText,
  Plus,
  Edit,
  Trash2,
  Search,
  Loader2,
  AlertCircle,
  Image as ImageIcon,
  Eye,
  EyeOff,
  Star,
  StarOff,
} from 'lucide-react';
import TemplateForm from '@/components/admin/TemplateForm';

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
  created_at: string;
  updated_at: string;
  created_by_email?: string;
}

export default function AdminTemplatesPage() {
  const { isAuthenticated } = useAdminAuth();
  const [templates, setTemplates] = useState<PosterTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<PosterTemplate | null>(null);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PosterTemplate | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      loadTemplates();
    }
  }, [isAuthenticated]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Don't filter by is_active in admin panel - show all templates
      const response = await fetch('/api/admin/templates', {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || `Failed to load templates: ${response.statusText}`);
      }

      const data = await response.json();
      // Handle both list and paginated responses
      const templatesList = Array.isArray(data) ? data : (data.results || []);
      setTemplates(templatesList);
    } catch (err) {
      console.error('Error loading templates:', err);
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTemplate) return;

    try {
      const response = await fetch(`/api/admin/templates/${selectedTemplate.id}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || 'Failed to delete template');
      }

      setTemplates(templates.filter(t => t.id !== selectedTemplate.id));
      setDeleteDialogOpen(false);
      setSelectedTemplate(null);
    } catch (err) {
      console.error('Error deleting template:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete template');
    }
  };

  const handleToggleActive = async (template: PosterTemplate) => {
    try {
      const response = await fetch(`/api/admin/templates/${template.id}`, {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !template.is_active }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || 'Failed to update template');
      }

      const updated = await response.json();
      setTemplates(templates.map(t => t.id === template.id ? updated : t));
    } catch (err) {
      console.error('Error updating template:', err);
      setError(err instanceof Error ? err.message : 'Failed to update template');
    }
  };

  const handleToggleFeatured = async (template: PosterTemplate) => {
    try {
      const response = await fetch(`/api/admin/templates/${template.id}`, {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_featured: !template.is_featured }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || 'Failed to update template');
      }

      const updated = await response.json();
      setTemplates(templates.map(t => t.id === template.id ? updated : t));
    } catch (err) {
      console.error('Error updating template:', err);
      setError(err instanceof Error ? err.message : 'Failed to update template');
    }
  };

  const handleCreate = () => {
    setEditingTemplate(null);
    setFormDialogOpen(true);
  };

  const handleEdit = (template: PosterTemplate) => {
    setEditingTemplate(template);
    setFormDialogOpen(true);
  };

  const handleFormSuccess = () => {
    setFormDialogOpen(false);
    setEditingTemplate(null);
    loadTemplates();
  };

  // Get unique categories
  const categories = ['All', ...Array.from(new Set(templates.map(t => t.category).filter(Boolean)))];
  
  // Get unique subcategories (filtered by selected category if not 'All')
  const subcategories = useMemo(() => {
    const filtered = selectedCategory === 'All' 
      ? templates 
      : templates.filter(t => t.category === selectedCategory);
    const subs = Array.from(new Set(filtered.map(t => t.subcategory).filter(Boolean)));
    return ['All', ...subs];
  }, [templates, selectedCategory]);

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.subcategory.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
    const matchesSubcategory = selectedSubcategory === 'All' || template.subcategory === selectedSubcategory;
    const matchesStatus = 
      selectedStatus === 'All' ||
      (selectedStatus === 'Active' && template.is_active) ||
      (selectedStatus === 'Inactive' && !template.is_active);
    
    return matchesSearch && matchesCategory && matchesSubcategory && matchesStatus;
  });

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Template Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage poster templates, prompts, and thumbnails
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search templates..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <select
                className="w-full p-2 border rounded-md"
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setSelectedSubcategory('All'); // Reset subcategory when category changes
                }}
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Subcategory</Label>
              <select
                className="w-full p-2 border rounded-md"
                value={selectedSubcategory}
                onChange={(e) => setSelectedSubcategory(e.target.value)}
              >
                {subcategories.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <select
                className="w-full p-2 border rounded-md"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                <option value="All">All</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Templates Grid */}
      {loading ? (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          </CardContent>
        </Card>
      ) : filteredTemplates.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No templates found</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <CardDescription className="mt-1 line-clamp-2">
                      {template.description || 'No description'}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1 ml-2">
                    {template.is_featured && (
                      <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                        <Star className="h-3 w-3 mr-1" />
                        Featured
                      </Badge>
                    )}
                    {!template.is_active && (
                      <Badge variant="secondary" className="bg-gray-100 text-gray-800">
                        Inactive
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Thumbnail */}
                {template.thumbnail_url ? (
                  <div className="aspect-[4/3] rounded-lg overflow-hidden mb-4 bg-muted">
                    <img
                      src={template.thumbnail_url}
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="aspect-[4/3] rounded-lg bg-muted flex items-center justify-center mb-4">
                    <ImageIcon className="h-12 w-12 text-muted-foreground" />
                  </div>
                )}

                {/* Metadata */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    {template.category && (
                      <Badge variant="outline">{template.category}</Badge>
                    )}
                    {template.subcategory && (
                      <Badge variant="secondary">{template.subcategory}</Badge>
                    )}
                  </div>
                  {template.audience && template.audience.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium">Audience:</span>
                      {template.audience.map((aud, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {aud}
                        </Badge>
                      ))}
                    </div>
                  )}
                  {template.offer && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">Offer:</span>
                      {template.offer !== 'No Offer' ? (
                        <Badge className="bg-orange-100 text-orange-800">{template.offer}</Badge>
                      ) : (
                        <Badge variant="outline" className="text-gray-600">No Offer</Badge>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(template)}
                    className="flex-1"
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleToggleActive(template)}
                    title={template.is_active ? 'Deactivate' : 'Activate'}
                  >
                    {template.is_active ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleToggleFeatured(template)}
                    title={template.is_featured ? 'Unfeature' : 'Feature'}
                  >
                    {template.is_featured ? (
                      <Star className="h-4 w-4 text-yellow-600" />
                    ) : (
                      <StarOff className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      setSelectedTemplate(template);
                      setDeleteDialogOpen(true);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Template</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{selectedTemplate?.name}&quot;? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Form Dialog */}
      <Dialog open={formDialogOpen} onOpenChange={setFormDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingTemplate ? 'Edit Template' : 'Create Template'}
            </DialogTitle>
            <DialogDescription>
              {editingTemplate ? 'Update template details' : 'Create a new poster template'}
            </DialogDescription>
          </DialogHeader>
          <TemplateForm
            template={editingTemplate}
            onSuccess={handleFormSuccess}
            onCancel={() => {
              setFormDialogOpen(false);
              setEditingTemplate(null);
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

