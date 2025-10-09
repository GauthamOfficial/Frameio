"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  Upload, 
  Wand2, 
  Calendar, 
  Share2, 
  Download, 
  X, 
  Sparkles, 
  Palette, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2
} from "lucide-react"
import React, { useState, useRef, useEffect } from "react"
import { useToastHelpers } from "@/components/common"
import { useAppContext } from "@/contexts/app-context"
import { apiClient } from "@/lib/api-client"
import { nanoBananaService } from "@/lib/ai/nanobanana"
import { generateTextilePrompt, extractKeywordsFromInput, suggestPromptImprovements } from "@/lib/ai/promptUtils"
import ColorPaletteExtractor, { ColorInfo } from "@/components/ColorPaletteExtractor"
import TemplateRecommender, { Template } from "@/components/TemplateRecommender"

interface GeneratedPoster {
  url: string
  captions: string[]
  hashtags: string[]
  metadata?: {
    prompt: string
    generated_at: string
    ai_service: string
  }
}

interface ScheduleData {
  platform: 'instagram' | 'facebook' | 'twitter' | 'linkedin'
  scheduledTime: string
  caption: string
}

export default function EnhancedPosterGenerator() {
  const { showSuccess, showError } = useToastHelpers()
  const appContext = useAppContext()
  const { token } = appContext || { token: null }
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Set token in API client
  React.useEffect(() => {
    if (token) {
      apiClient.setToken(token)
    }
  }, [token])
  
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [isScheduling, setIsScheduling] = useState(false)
  const [isPosting, setIsPosting] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [selectedStyle, setSelectedStyle] = useState("")
  const [selectedFabric, setSelectedFabric] = useState("")
  const [selectedOccasion, setSelectedOccasion] = useState("")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [generatedPoster, setGeneratedPoster] = useState<GeneratedPoster | null>(null)
  const [extractedColors, setExtractedColors] = useState<ColorInfo[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [scheduleData, setScheduleData] = useState<ScheduleData>({
    platform: 'instagram',
    scheduledTime: '',
    caption: ''
  })
  const [aiServiceStatus, setAiServiceStatus] = useState<'available' | 'fallback' | 'error'>('available')
  const [promptSuggestions, setPromptSuggestions] = useState<string[]>([])

  // Check AI service availability
  useEffect(() => {
    const checkAiService = () => {
      if (nanoBananaService.isConfigured()) {
        setAiServiceStatus('available')
      } else {
        setAiServiceStatus('fallback')
      }
    }
    checkAiService()
  }, [])

  // Generate prompt suggestions when user types
  useEffect(() => {
    if (prompt.length > 10) {
      const suggestions = suggestPromptImprovements(prompt)
      setPromptSuggestions(suggestions)
    } else {
      setPromptSuggestions([])
    }
  }, [prompt])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    
    // Validate files using API client
    const validation = apiClient.validateMultipleFiles(files)
    if (!validation.valid) {
      validation.errors.forEach(error => showError(error))
      return
    }
    
    setUploadedFiles(prev => [...prev, ...files])
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFileToServer = async (file: File): Promise<string> => {
    try {
      const result = await apiClient.uploadFile(file)
      if (!result.success) {
        console.warn('File upload failed, using fallback:', result.error)
        // Return a data URL as fallback
        return new Promise((resolve) => {
          const reader = new FileReader()
          reader.onload = () => resolve(reader.result as string)
          reader.readAsDataURL(file)
        })
      }
      return result.data!.url
    } catch (error) {
      console.warn('File upload error, using fallback:', error)
      // Return a data URL as fallback
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(file)
      })
    }
  }

  const handleGenerateWithAI = async () => {
    if (!prompt.trim()) {
      showError("Please enter a prompt for the poster generation")
      return
    }

    setIsGenerating(true)
    setAiServiceStatus('available')

    try {
      // Generate enhanced prompt using AI utilities
      const textilePrompt = generateTextilePrompt({
        theme: prompt,
        color: extractedColors.length > 0 ? extractedColors[0].hex : undefined,
        style: selectedStyle || 'modern',
        fabric: selectedFabric || 'cotton',
        occasion: selectedOccasion || 'casual',
        additionalKeywords: promptSuggestions
      })

      // Try NanoBanana API first
      const aiResponse = await nanoBananaService.generateImage(
        textilePrompt.enhancedPrompt,
        {
          style: selectedStyle,
          aspect_ratio: '1:1',
          quality: 'hd'
        }
      )

      if (aiResponse.success && aiResponse.image_url) {
        // AI generation successful
        setGeneratedPoster({
          url: aiResponse.image_url,
          captions: [
            `Discover our ${selectedFabric || 'textile'} collection`,
            `Perfect for ${selectedOccasion || 'any occasion'}`,
            `Style: ${selectedStyle || 'modern'} design`
          ],
          hashtags: [
            `#${selectedFabric || 'textile'}`,
            `#${selectedStyle || 'modern'}`,
            '#fashion',
            '#design',
            '#textile'
          ],
          metadata: {
            prompt: textilePrompt.enhancedPrompt,
            generated_at: new Date().toISOString(),
            ai_service: 'nanobanana'
          }
        })
        setAiServiceStatus('available')
        showSuccess("AI poster generated successfully!")
      } else {
        // Fallback to backend API - this will generate fresh content
        console.log('NanoBanana API not available, using backend generation')
        await handleGenerateWithBackend(textilePrompt.enhancedPrompt)
      }
    } catch (error) {
      console.error('AI generation failed:', error)
      setAiServiceStatus('error')
      
      // Try backend fallback
      try {
        await handleGenerateWithBackend(prompt)
      } catch (fallbackError) {
        console.error('Backend fallback also failed:', fallbackError)
        // Final fallback to frontend-only generation
        try {
          await handleFrontendOnlyGeneration(prompt)
        } catch (finalError) {
          showError(`Failed to generate poster: ${error instanceof Error ? error.message : 'Unknown error'}`)
        }
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleFrontendOnlyGeneration = async (enhancedPrompt: string) => {
    // Frontend-only generation when backend is unavailable
    console.log('Using frontend-only generation')
    
    // Generate a unique image URL
    const timestamp = Date.now()
    const uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp}&text=AI+Generated+${selectedFabric || 'Textile'}+Poster`
    
    // Generate dynamic captions
    const dynamicCaptions = [
      `✨ ${enhancedPrompt.split(',')[0]} ✨`,
      `Perfect for ${selectedOccasion || 'any occasion'}`,
      `Style: ${selectedStyle || 'modern'} design`,
      `Fabric: ${selectedFabric || 'textile'} collection`
    ]
    
    // Generate dynamic hashtags
    const dynamicHashtags = [
      `#${selectedFabric || 'textile'}`,
      `#${selectedStyle || 'modern'}`,
      `#${selectedOccasion || 'fashion'}`,
      '#fashion',
      '#design',
      '#textile',
      '#ai_generated',
      '#frontend_generated'
    ]
    
    setGeneratedPoster({
      url: uniqueImageUrl,
      captions: dynamicCaptions,
      hashtags: dynamicHashtags,
      metadata: {
        prompt: enhancedPrompt,
        generated_at: new Date().toISOString(),
        ai_service: 'frontend_fallback',
        unique_id: `frontend_gen_${timestamp}`
      }
    })
    
    setAiServiceStatus('fallback')
    showSuccess("Poster generated using frontend service!")
  }

  const handleGenerateWithBackend = async (enhancedPrompt: string) => {
    let productImageUrl = ''
    
    // Try to upload files if available, but don't fail if upload doesn't work
    if (uploadedFiles.length > 0) {
      try {
        const uploadedUrls = await Promise.all(
          uploadedFiles.map(file => uploadFileToServer(file))
        )
        productImageUrl = uploadedUrls[0]
        console.log('Files uploaded successfully:', uploadedUrls.length)
      } catch (error) {
        console.warn('File upload failed, proceeding without uploaded images:', error)
        // Continue without uploaded images
      }
    }
    
    // If no uploaded images, use a placeholder or generate without image
    if (!productImageUrl) {
      productImageUrl = 'https://via.placeholder.com/512x512/FF6B6B/FFFFFF?text=AI+Generated+Poster'
      console.log('Using placeholder image for generation')
    }
    
    // Generate poster using backend AI service
    let result
    try {
      result = await apiClient.generatePoster({
        product_image_url: productImageUrl,
        fabric_type: selectedFabric as any || 'cotton',
        festival: selectedOccasion as any || 'general',
        price_range: '₹2999',
        style: selectedStyle as any || 'modern',
        custom_text: enhancedPrompt,
        offer_details: 'Special offer available'
      })
    } catch (error) {
      console.warn('Backend API unavailable, using frontend fallback:', error)
      // Fallback to frontend-only generation
      return handleFrontendOnlyGeneration(enhancedPrompt)
    }
    
    if (!result.success) {
      console.warn('Backend generation failed, using frontend fallback:', result.error)
      // Fallback to frontend-only generation
      return handleFrontendOnlyGeneration(enhancedPrompt)
    }
    
    const data = result.data!
    
    // Generate dynamic captions based on the prompt and selections
    const dynamicCaptions = [
      `✨ ${enhancedPrompt.split(',')[0]} ✨`,
      `Perfect for ${selectedOccasion || 'any occasion'}`,
      `Style: ${selectedStyle || 'modern'} design`,
      `Fabric: ${selectedFabric || 'textile'} collection`
    ]
    
    // Generate dynamic hashtags
    const dynamicHashtags = [
      `#${selectedFabric || 'textile'}`,
      `#${selectedStyle || 'modern'}`,
      `#${selectedOccasion || 'fashion'}`,
      '#fashion',
      '#design',
      '#textile',
      '#ai_generated'
    ]
    
    setGeneratedPoster({
      url: data.poster_url,
      captions: data.caption_suggestions?.length > 0 ? data.caption_suggestions : dynamicCaptions,
      hashtags: data.hashtags?.length > 0 ? data.hashtags : dynamicHashtags,
      metadata: {
        prompt: enhancedPrompt,
        generated_at: new Date().toISOString(),
        ai_service: 'backend',
        unique_id: data.metadata?.unique_id || `gen_${Date.now()}`
      }
    })
    
    setAiServiceStatus('fallback')
    showSuccess("Poster generated using backend service!")
  }

  const handleDownload = async () => {
    if (!generatedPoster) {
      showError("No poster to download")
      return
    }
    
    setIsDownloading(true)
    try {
      const success = await apiClient.downloadFile(
        generatedPoster.url, 
        `ai-poster-${Date.now()}.png`
      )
      
      if (success) {
        showSuccess("Poster downloaded successfully!")
      } else {
        throw new Error('Download failed')
      }
    } catch (error) {
      showError(`Failed to download poster: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleSchedule = () => {
    if (!generatedPoster) {
      showError("Please generate a poster first")
      return
    }
    setShowScheduleModal(true)
  }

  const handleScheduleSubmit = async () => {
    if (!scheduleData.scheduledTime || !scheduleData.caption) {
      showError("Please fill in all required fields")
      return
    }
    
    setIsScheduling(true)
    try {
      const result = await apiClient.schedulePost({
        platform: scheduleData.platform,
        asset_url: generatedPoster.url,
        caption: scheduleData.caption,
        scheduled_time: scheduleData.scheduledTime,
        metadata: {
          hashtags: generatedPoster.hashtags,
          generated_at: new Date().toISOString(),
          ai_service: generatedPoster.metadata?.ai_service
        }
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to schedule post')
      }
      
      showSuccess("Post scheduled successfully!")
      setShowScheduleModal(false)
      setScheduleData({ platform: 'instagram', scheduledTime: '', caption: '' })
    } catch (error) {
      showError(`Failed to schedule post: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsScheduling(false)
    }
  }

  const handlePostNow = async () => {
    if (!generatedPoster) {
      showError("Please generate a poster first")
      return
    }
    
    setIsPosting(true)
    try {
      const result = await apiClient.postToSocialMedia({
        platform: 'instagram',
        asset_url: generatedPoster.url,
        caption: generatedPoster.captions[0] || 'Check out this amazing AI-generated textile design!',
        metadata: {
          hashtags: generatedPoster.hashtags,
          ai_service: generatedPoster.metadata?.ai_service
        }
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to post to social media')
      }
      
      showSuccess("Posted to social media successfully!")
    } catch (error) {
      showError(`Failed to post: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsPosting(false)
    }
  }

  const handleColorExtracted = (colors: ColorInfo[]) => {
    setExtractedColors(colors)
  }

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template)
    showSuccess(`Template "${template.name}" selected for reference`)
  }

  const styles = [
    { id: "modern", label: "Modern" },
    { id: "traditional", label: "Traditional" },
    { id: "elegant", label: "Elegant" },
    { id: "minimalist", label: "Minimalist" },
    { id: "bohemian", label: "Bohemian" },
  ]

  const fabrics = [
    { id: "cotton", label: "Cotton" },
    { id: "silk", label: "Silk" },
    { id: "saree", label: "Saree" },
    { id: "linen", label: "Linen" },
    { id: "wool", label: "Wool" },
    { id: "denim", label: "Denim" },
  ]

  const occasions = [
    { id: "casual", label: "Casual" },
    { id: "festival", label: "Festival" },
    { id: "wedding", label: "Wedding" },
    { id: "formal", label: "Formal" },
    { id: "party", label: "Party" },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI-Powered Poster Generator</h1>
          <p className="text-muted-foreground mt-1">
            Create stunning textile marketing posters with advanced AI assistance.
          </p>
        </div>
        
        {/* AI Service Status */}
        <div className="flex items-center gap-2">
          {aiServiceStatus === 'available' && (
            <Badge variant="default" className="bg-green-100 text-green-800">
              <CheckCircle className="h-3 w-3 mr-1" />
              AI Ready
            </Badge>
          )}
          {aiServiceStatus === 'fallback' && (
            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
              <AlertCircle className="h-3 w-3 mr-1" />
              Fallback Mode
            </Badge>
          )}
          {aiServiceStatus === 'error' && (
            <Badge variant="destructive">
              <AlertCircle className="h-3 w-3 mr-1" />
              AI Error
            </Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column - Configuration */}
        <div className="xl:col-span-1 space-y-6">
          {/* Upload Section */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Upload & Configure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* File Upload */}
              <div className="space-y-2">
                <Label htmlFor="upload">Upload Images (Optional)</Label>
                <div 
                  className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-accent transition-colors cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drag and drop images here, or click to browse
                  </p>
                  <Button variant="outline" size="sm" type="button">
                    Choose Files
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
                
                {/* Uploaded Files */}
                {uploadedFiles.length > 0 && (
                  <div className="space-y-2">
                    <Label>Uploaded Files ({uploadedFiles.length})</Label>
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-muted rounded-lg">
                          <div className="flex items-center space-x-2">
                            <div className="w-6 h-6 bg-primary/10 rounded flex items-center justify-center">
                              <Upload className="h-3 w-3 text-primary" />
                            </div>
                            <div>
                              <p className="text-xs font-medium">{file.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(index)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* AI Prompt Input */}
              <div className="space-y-2">
                <Label htmlFor="prompt">AI Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe your textile design: 'Elegant silk saree with gold patterns for wedding collection'..."
                  className="min-h-[100px]"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
                
                {/* Prompt Suggestions */}
                {promptSuggestions.length > 0 && (
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">Suggestions:</Label>
                    {promptSuggestions.map((suggestion, index) => (
                      <p key={index} className="text-xs text-muted-foreground bg-muted p-2 rounded">
                        {suggestion}
                      </p>
                    ))}
                  </div>
                )}
              </div>

              {/* Style Options */}
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label>Style</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {styles.map((style) => (
                      <Button
                        key={style.id}
                        variant={selectedStyle === style.id ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedStyle(style.id)}
                      >
                        {style.label}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Fabric</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {fabrics.map((fabric) => (
                      <Button
                        key={fabric.id}
                        variant={selectedFabric === fabric.id ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedFabric(fabric.id)}
                      >
                        {fabric.label}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Occasion</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {occasions.map((occasion) => (
                      <Button
                        key={occasion.id}
                        variant={selectedOccasion === occasion.id ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedOccasion(occasion.id)}
                      >
                        {occasion.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Generate Button */}
              <Button 
                className="w-full bg-textile-accent"
                onClick={handleGenerateWithAI}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating with AI...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate with AI
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Color Palette Extractor */}
          {generatedPoster && (
            <ColorPaletteExtractor
              imageUrl={generatedPoster.url}
              onPaletteExtracted={handleColorExtracted}
            />
          )}
        </div>

        {/* Middle Column - Preview */}
        <div className="xl:col-span-1">
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>AI Generated Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-[4/5] bg-muted rounded-lg flex items-center justify-center mb-4 overflow-hidden">
                {generatedPoster ? (
                  <img
                    src={generatedPoster.url}
                    alt="AI Generated poster"
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="text-center">
                    <Sparkles className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">AI-generated poster will appear here</p>
                  </div>
                )}
              </div>
              
              {/* Generated Content Info */}
              {generatedPoster && (
                <div className="space-y-3 mb-4">
                  {generatedPoster.metadata && (
                    <div className="text-xs text-muted-foreground">
                      Generated with {generatedPoster.metadata.ai_service} • {new Date(generatedPoster.metadata.generated_at).toLocaleString()}
                    </div>
                  )}
                  
                  {generatedPoster.captions.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium">AI Captions:</Label>
                      <div className="space-y-1">
                        {generatedPoster.captions.slice(0, 2).map((caption, index) => (
                          <p key={index} className="text-sm text-muted-foreground bg-muted p-2 rounded">
                            {caption}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {generatedPoster.hashtags.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium">Hashtags:</Label>
                      <div className="flex flex-wrap gap-1">
                        {generatedPoster.hashtags.slice(0, 8).map((hashtag, index) => (
                          <span key={index} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                            {hashtag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleSchedule}
                  disabled={!generatedPoster || isScheduling}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {isScheduling ? "Scheduling..." : "Schedule"}
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handlePostNow}
                  disabled={!generatedPoster || isPosting}
                >
                  <Share2 className="mr-2 h-4 w-4" />
                  {isPosting ? "Posting..." : "Post Now"}
                </Button>
              </div>
              
              <Button 
                variant="outline" 
                className="w-full mt-3"
                onClick={handleDownload}
                disabled={!generatedPoster || isDownloading}
              >
                <Download className="mr-2 h-4 w-4" />
                {isDownloading ? "Downloading..." : "Download"}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - AI Recommendations */}
        <div className="xl:col-span-1">
          <TemplateRecommender
            theme={prompt}
            colorPalette={extractedColors}
            style={selectedStyle}
            onTemplateSelect={handleTemplateSelect}
          />
        </div>
      </div>
      
      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Schedule Post</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="platform">Platform</Label>
                <select
                  id="platform"
                  value={scheduleData.platform}
                  onChange={(e) => setScheduleData(prev => ({ ...prev, platform: e.target.value as any }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="twitter">Twitter</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="scheduledTime">Scheduled Time</Label>
                <Input
                  id="scheduledTime"
                  type="datetime-local"
                  value={scheduleData.scheduledTime}
                  onChange={(e) => setScheduleData(prev => ({ ...prev, scheduledTime: e.target.value }))}
                  min={new Date().toISOString().slice(0, 16)}
                />
              </div>
              
              <div>
                <Label htmlFor="caption">Caption</Label>
                <Textarea
                  id="caption"
                  value={scheduleData.caption}
                  onChange={(e) => setScheduleData(prev => ({ ...prev, caption: e.target.value }))}
                  placeholder="Enter your post caption..."
                  rows={3}
                />
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => setShowScheduleModal(false)}
                >
                  Cancel
                </Button>
                <Button 
                  className="flex-1"
                  onClick={handleScheduleSubmit}
                  disabled={isScheduling}
                >
                  {isScheduling ? "Scheduling..." : "Schedule"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
