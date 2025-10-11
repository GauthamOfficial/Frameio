"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useToastHelpers } from '@/components/common'
import { useAppContext } from '@/contexts/app-context'
import { apiClient } from '@/lib/api-client'
import { 
  Wand2, 
  Hash, 
  Smile, 
  Target, 
  Users, 
  TrendingUp, 
  Copy, 
  Download, 
  Share2,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Loader2,
  Image as ImageIcon,
  Upload,
  X
} from 'lucide-react'

interface GeneratedPost {
  main_content: string
  hashtags: string[]
  call_to_action: string
  word_count: number
  character_count: number
  post_type: string
  engagement_score: number
  generated_images?: string[]
  image_urls?: string[]
}

interface PostTemplate {
  id: string
  name: string
  description: string
  post_type: string
  style: string
  tone: string
  length: string
  platform?: string
  example_prompt?: string
}

interface GenerationRequest {
  prompt: string
  post_type: string
  style: string
  tone: string
  length: string
  include_hashtags: boolean
  include_emoji: boolean
  platform?: string
  target_audience?: string
  call_to_action?: string
  generate_images?: boolean
  image_style?: string
  image_quality?: string
}

export default function AIImagePostGenerator() {
  const { showSuccess, showError } = useToastHelpers()
  const appContext = useAppContext()
  const { token } = appContext || { token: null }
  
  // Set token in API client
  useEffect(() => {
    if (token) {
      apiClient.setToken(token)
    }
  }, [token])
  
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false)
  const [generatedPost, setGeneratedPost] = useState<GeneratedPost | null>(null)
  const [templates, setTemplates] = useState<PostTemplate[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<PostTemplate | null>(null)
  const [generationStep, setGenerationStep] = useState<'idle' | 'generating' | 'completed'>('idle')
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  
  // Form state
  const [request, setRequest] = useState<GenerationRequest>({
    prompt: '',
    post_type: 'social_media',
    style: 'modern',
    tone: 'professional',
    length: 'medium',
    include_hashtags: true,
    include_emoji: true,
    platform: 'instagram',
    target_audience: '',
    call_to_action: '',
    generate_images: true,
    image_style: 'photorealistic',
    image_quality: 'high'
  })
  
  // Load templates on component mount
  useEffect(() => {
    loadTemplates()
  }, [])
  
  const loadTemplates = async () => {
    setIsLoadingTemplates(true)
    try {
      const response = await apiClient.get('/api/ai/post-generation/get_post_templates/')
      if (response.success) {
        setTemplates(response.templates)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setIsLoadingTemplates(false)
    }
  }
  
  const handleTemplateSelect = (template: PostTemplate) => {
    setSelectedTemplate(template)
    setRequest(prev => ({
      ...prev,
      post_type: template.post_type,
      style: template.style,
      tone: template.tone,
      length: template.length,
      platform: template.platform
    }))
    
    if (template.example_prompt) {
      setRequest(prev => ({
        ...prev,
        prompt: template.example_prompt || ''
      }))
    }
  }
  
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files])
      
      // Create preview URLs
      const newPreviewUrls = files.map(file => URL.createObjectURL(file))
      setPreviewUrls(prev => [...prev, ...newPreviewUrls])
    }
  }
  
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
    setPreviewUrls(prev => {
      const newUrls = [...prev]
      URL.revokeObjectURL(newUrls[index])
      return newUrls.filter((_, i) => i !== index)
    })
  }
  
  const handleGenerate = async () => {
    if (!request.prompt.trim()) {
      showError("Please enter a prompt for the post generation")
      return
    }
    
    setIsGenerating(true)
    setGenerationStep('generating')
    
    try {
      let response
      
      console.log('🚀 Starting AI generation with request:', request)
      console.log('📁 Uploaded files:', uploadedFiles.length)
      console.log('🖼️ Generate images:', request.generate_images)
      
      if (uploadedFiles.length > 0 && request.generate_images) {
        // Generate post with images using the image-based endpoint
        const formData = new FormData()
        formData.append('prompt', request.prompt)
        formData.append('post_type', request.post_type)
        formData.append('style', request.style)
        formData.append('tone', request.tone)
        formData.append('platform', request.platform || 'instagram')
        
        // Append uploaded files
        uploadedFiles.forEach(file => {
          formData.append('images', file)
        })
        
        console.log('📤 Calling generate_image_post endpoint with FormData')
        response = await apiClient.post('/api/ai/post-generation/generate_image_post/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        console.log('📥 Image post response:', response)
      } else if (request.platform) {
        // Generate platform-specific post
        console.log('📤 Calling generate_social_media_post endpoint')
        response = await apiClient.post('/api/ai/post-generation/generate_social_media_post/', {
          prompt: request.prompt,
          platform: request.platform,
          target_audience: request.target_audience,
          call_to_action: request.call_to_action,
          generate_images: request.generate_images,
          image_style: request.image_style,
          image_quality: request.image_quality
        })
      } else {
        // Generate general post
        console.log('📤 Calling generate_text_post endpoint')
        response = await apiClient.post('/api/ai/post-generation/generate_text_post/', {
          prompt: request.prompt,
          post_type: request.post_type,
          style: request.style,
          tone: request.tone,
          length: request.length,
          include_hashtags: request.include_hashtags,
          include_emoji: request.include_emoji,
          target_audience: request.target_audience,
          call_to_action: request.call_to_action,
          generate_images: request.generate_images,
          image_style: request.image_style,
          image_quality: request.image_quality
        })
      }
      
      if (response.success) {
        // Merge content with images at top level
        const postData = {
          ...response.content,
          generated_images: response.generated_images || response.content.generated_images || [],
          image_urls: response.image_urls || response.content.image_urls || []
        }
        setGeneratedPost(postData)
        setGenerationStep('completed')
        showSuccess("Post generated successfully!")
        console.log('Generated post data:', postData)
      } else {
        throw new Error(response.error || 'Generation failed')
      }
    } catch (error) {
      console.error('❌ API call failed:', error)
      console.error('❌ Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      })
      showError(`Failed to generate post: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setGenerationStep('idle')
    } finally {
      setIsGenerating(false)
    }
  }
  
  const handleCopyContent = (content: string) => {
    navigator.clipboard.writeText(content)
    showSuccess("Content copied to clipboard!")
  }
  
  const handleCopyHashtags = () => {
    if (generatedPost?.hashtags) {
      const hashtagsText = generatedPost.hashtags.join(' ')
      navigator.clipboard.writeText(hashtagsText)
      showSuccess("Hashtags copied to clipboard!")
    }
  }
  
  const handleDownload = () => {
    if (!generatedPost) return
    
    const content = `
${generatedPost.main_content}

${generatedPost.hashtags.join(' ')}

${generatedPost.call_to_action}

---
Generated on: ${new Date().toLocaleString()}
Post Type: ${generatedPost.post_type}
Engagement Score: ${generatedPost.engagement_score}/10
Word Count: ${generatedPost.word_count}
Character Count: ${generatedPost.character_count}
    `.trim()
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ai-post-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    showSuccess("Post content downloaded!")
  }
  
  const handleShare = () => {
    if (!generatedPost) return
    
    const shareText = `${generatedPost.main_content}\n\n${generatedPost.hashtags.join(' ')}`
    
    if (navigator.share) {
      navigator.share({
        title: 'AI Generated Post',
        text: shareText
      })
    } else {
      navigator.clipboard.writeText(shareText)
      showSuccess("Post content copied to clipboard for sharing!")
    }
  }
  
  const handleRegenerate = () => {
    setGeneratedPost(null)
    setGenerationStep('idle')
    handleGenerate()
  }
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Image Post Generator</h1>
          <p className="text-muted-foreground mt-1">
            Generate engaging social media posts with AI-generated images
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={loadTemplates}
            disabled={isLoadingTemplates}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoadingTemplates ? 'animate-spin' : ''}`} />
            Refresh Templates
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Generation Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Template Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Post Templates
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingTemplates ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span className="ml-2">Loading templates...</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map((template) => (
                    <Card 
                      key={template.id}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        selectedTemplate?.id === template.id 
                          ? 'ring-2 ring-primary bg-primary/5' 
                          : 'hover:bg-muted/50'
                      }`}
                      onClick={() => handleTemplateSelect(template)}
                    >
                      <CardContent className="p-4">
                        <h3 className="font-semibold">{template.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {template.description}
                        </p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          <Badge variant="secondary" className="text-xs">
                            {template.style}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {template.tone}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {template.length}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Generation Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="h-5 w-5" />
                Generate Post with Images
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Prompt Input */}
              <div className="space-y-2">
                <Label htmlFor="prompt">Post Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe what you want to post about..."
                  value={request.prompt}
                  onChange={(e) => setRequest(prev => ({ ...prev, prompt: e.target.value }))}
                  rows={4}
                />
              </div>
              
              {/* Image Upload */}
              <div className="space-y-2">
                <Label>Upload Images (Optional)</Label>
                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
                  <div className="flex flex-col items-center justify-center space-y-4">
                    <Upload className="h-8 w-8 text-muted-foreground" />
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">
                        Drop images here or click to upload
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Supports JPG, PNG, GIF up to 10MB each
                      </p>
                    </div>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="image-upload"
                    />
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('image-upload')?.click()}
                    >
                      <ImageIcon className="mr-2 h-4 w-4" />
                      Choose Images
                    </Button>
                  </div>
                </div>
                
                {/* Preview uploaded images */}
                {previewUrls.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
                    {previewUrls.map((url, index) => (
                      <div key={index} className="relative">
                        <img
                          src={url}
                          alt={`Preview ${index + 1}`}
                          className="w-full h-24 object-cover rounded-lg"
                        />
                        <Button
                          variant="destructive"
                          size="sm"
                          className="absolute -top-2 -right-2 h-6 w-6 p-0"
                          onClick={() => removeFile(index)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Platform Selection */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select 
                    value={request.platform} 
                    onValueChange={(value: string) => setRequest(prev => ({ ...prev, platform: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="facebook">Facebook</SelectItem>
                      <SelectItem value="twitter">Twitter</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="post_type">Post Type</Label>
                  <Select 
                    value={request.post_type} 
                    onValueChange={(value: string) => setRequest(prev => ({ ...prev, post_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select post type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="social_media">Social Media</SelectItem>
                      <SelectItem value="blog">Blog</SelectItem>
                      <SelectItem value="announcement">Announcement</SelectItem>
                      <SelectItem value="promotional">Promotional</SelectItem>
                      <SelectItem value="educational">Educational</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              {/* Style and Tone */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="style">Style</Label>
                  <Select 
                    value={request.style} 
                    onValueChange={(value: string) => setRequest(prev => ({ ...prev, style: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select style" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="modern">Modern</SelectItem>
                      <SelectItem value="traditional">Traditional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="formal">Formal</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="tone">Tone</Label>
                  <Select 
                    value={request.tone} 
                    onValueChange={(value: string) => setRequest(prev => ({ ...prev, tone: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select tone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="authoritative">Authoritative</SelectItem>
                      <SelectItem value="conversational">Conversational</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="length">Length</Label>
                  <Select 
                    value={request.length} 
                    onValueChange={(value: string) => setRequest(prev => ({ ...prev, length: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select length" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="short">Short</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="long">Long</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              {/* Image Generation Options */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="generate_images"
                    checked={request.generate_images}
                    onChange={(e) => setRequest(prev => ({ ...prev, generate_images: e.target.checked }))}
                    className="rounded"
                  />
                  <Label htmlFor="generate_images" className="flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Generate AI Images
                  </Label>
                </div>
                
                {request.generate_images && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="image_style">Image Style</Label>
                      <Select 
                        value={request.image_style} 
                        onValueChange={(value: string) => setRequest(prev => ({ ...prev, image_style: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select image style" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="photorealistic">Photorealistic</SelectItem>
                          <SelectItem value="artistic">Artistic</SelectItem>
                          <SelectItem value="minimalist">Minimalist</SelectItem>
                          <SelectItem value="vintage">Vintage</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="image_quality">Image Quality</Label>
                      <Select 
                        value={request.image_quality} 
                        onValueChange={(value: string) => setRequest(prev => ({ ...prev, image_quality: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select image quality" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="standard">Standard</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="ultra">Ultra</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Options */}
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="include_hashtags"
                    checked={request.include_hashtags}
                    onChange={(e) => setRequest(prev => ({ ...prev, include_hashtags: e.target.checked }))}
                    className="rounded"
                  />
                  <Label htmlFor="include_hashtags" className="flex items-center gap-2">
                    <Hash className="h-4 w-4" />
                    Include Hashtags
                  </Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="include_emoji"
                    checked={request.include_emoji}
                    onChange={(e) => setRequest(prev => ({ ...prev, include_emoji: e.target.checked }))}
                    className="rounded"
                  />
                  <Label htmlFor="include_emoji" className="flex items-center gap-2">
                    <Smile className="h-4 w-4" />
                    Include Emojis
                  </Label>
                </div>
              </div>
              
              {/* Target Audience */}
              <div className="space-y-2">
                <Label htmlFor="target_audience">Target Audience (Optional)</Label>
                <Input
                  id="target_audience"
                  placeholder="e.g., young professionals, fashion enthusiasts..."
                  value={request.target_audience}
                  onChange={(e) => setRequest(prev => ({ ...prev, target_audience: e.target.value }))}
                />
              </div>
              
              {/* Generate Button */}
              <Button 
                onClick={handleGenerate}
                disabled={isGenerating || !request.prompt.trim()}
                className="w-full"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate Post with Images
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
        
        {/* Right Column - Generated Content */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {generationStep === 'completed' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : generationStep === 'generating' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <AlertCircle className="h-5 w-5" />
                )}
                Generated Post
              </CardTitle>
            </CardHeader>
            <CardContent>
              {generatedPost ? (
                <div className="space-y-4">
                  {/* Main Content */}
                  <div className="space-y-2">
                    <Label>Post Content</Label>
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="whitespace-pre-wrap">{generatedPost.main_content}</p>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleCopyContent(generatedPost.main_content)}
                    >
                      <Copy className="mr-2 h-4 w-4" />
                      Copy Content
                    </Button>
                  </div>
                  
                  {/* Generated Images */}
                  {(generatedPost.generated_images || generatedPost.image_urls) && (
                    <div className="space-y-2">
                      <Label>Generated Images</Label>
                      <div className="grid grid-cols-1 gap-2">
                        {(generatedPost.generated_images || generatedPost.image_urls || []).map((imageUrl, index) => (
                          <div key={index} className="relative">
                            <img
                              src={imageUrl}
                              alt={`Generated image ${index + 1}`}
                              className="w-full h-32 object-cover rounded-lg"
                            />
                            <Button
                              variant="outline"
                              size="sm"
                              className="absolute top-2 right-2"
                              onClick={() => window.open(imageUrl, '_blank')}
                            >
                              <Download className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Hashtags */}
                  {generatedPost.hashtags.length > 0 && (
                    <div className="space-y-2">
                      <Label>Hashtags</Label>
                      <div className="flex flex-wrap gap-1">
                        {generatedPost.hashtags.map((hashtag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {hashtag}
                          </Badge>
                        ))}
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleCopyHashtags}
                      >
                        <Copy className="mr-2 h-4 w-4" />
                        Copy Hashtags
                      </Button>
                    </div>
                  )}
                  
                  {/* Call to Action */}
                  {generatedPost.call_to_action && (
                    <div className="space-y-2">
                      <Label>Call to Action</Label>
                      <div className="p-3 bg-muted rounded-lg">
                        <p>{generatedPost.call_to_action}</p>
                      </div>
                    </div>
                  )}
                  
                  <Separator />
                  
                  {/* Post Analytics */}
                  <div className="space-y-2">
                    <Label>Post Analytics</Label>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Words:</span>
                        <span className="ml-1 font-medium">{generatedPost.word_count}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Characters:</span>
                        <span className="ml-1 font-medium">{generatedPost.character_count}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Engagement:</span>
                        <span className="ml-1 font-medium">{generatedPost.engagement_score}/10</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Type:</span>
                        <span className="ml-1 font-medium capitalize">{generatedPost.post_type}</span>
                      </div>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  {/* Action Buttons */}
                  <div className="grid grid-cols-2 gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleDownload}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleShare}
                    >
                      <Share2 className="mr-2 h-4 w-4" />
                      Share
                    </Button>
                  </div>
                  
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={handleRegenerate}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Regenerate
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Wand2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    {generationStep === 'generating' 
                      ? 'Generating your post with images...' 
                      : 'Generated post with images will appear here'
                    }
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
