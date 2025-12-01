"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
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
  AlertCircle,
  CheckCircle,
  Loader2
} from "lucide-react"
import React, { useState, useRef, useEffect } from "react"
import { useToastHelpers } from "@/components/common"
import { useAppContext } from "@/contexts/app-context"
import { apiClient } from "@/lib/api-client"
import { nanoBananaService } from "@/lib/ai/nanobanana"
import { generateTextilePrompt } from "@/lib/ai/promptUtils"
import ColorPaletteExtractor, { ColorInfo } from "@/components/ColorPaletteExtractor"

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
  platform: 'instagram' | 'facebook' | 'tiktok' | 'whatsapp' | 'twitter' | 'linkedin'
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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isScheduling, setIsScheduling] = useState(false)
  const [isPosting, setIsPosting] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [generatedPoster, setGeneratedPoster] = useState<GeneratedPoster | null>(null)
  const [extractedColors, setExtractedColors] = useState<ColorInfo[]>([])
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [scheduleData, setScheduleData] = useState<ScheduleData>({
    platform: 'instagram',
    scheduledTime: '',
    caption: ''
  })
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [aiServiceStatus, setAiServiceStatus] = useState<'available' | 'error'>('available')
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [promptSuggestions, setPromptSuggestions] = useState<string[]>([])
  const [generationStep, setGenerationStep] = useState<'idle' | 'refining' | 'generating' | 'completed'>('idle')
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [refinedPrompt, setRefinedPrompt] = useState<string>('')
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [imageLoadError, setImageLoadError] = useState<boolean>(false)

  // Check AI service availability
  useEffect(() => {
    const checkAiService = () => {
      setAiServiceStatus(nanoBananaService.isConfigured() ? 'available' : 'error')
    }
    checkAiService()
  }, [])

  // Monitor generatedPoster state changes
  useEffect(() => {
    if (generatedPoster) {
      console.log('🔄 Generated poster updated:', generatedPoster)
      // Reset image load error when new poster is set
      setImageLoadError(false)
    }
  }, [generatedPoster])

  // Handle file uploads
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files])
      showSuccess(`Uploaded ${files.length} file(s)`)
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleGenerateWithAI = async () => {
    if (!prompt.trim()) {
      showError("Please enter a prompt")
      return
    }

    setIsGenerating(true)
    setGenerationError(null)
    setImageLoadError(false)
    setGenerationStep('refining')

    try {
      // Generate enhanced prompt
      const colorNames = extractedColors.map(c => c.name || c.hex).filter(Boolean) as string[]
      const promptParams = {
        theme: prompt,
        color: extractedColors[0]?.name || extractedColors[0]?.hex || undefined,
        fabric: 'cotton',
        occasion: 'casual',
        style: 'modern',
        additionalKeywords: colorNames
      }
      const textilePrompt = generateTextilePrompt(promptParams)
      const enhancedPrompt = textilePrompt.enhancedPrompt
      
      console.log('🎨 Enhanced prompt:', enhancedPrompt)
      
      // Try NanoBanana API first (only if properly configured)
      if (nanoBananaService.isConfigured()) {
        try {
          const aiResponse = await nanoBananaService.generateImage(
            enhancedPrompt,
            {
              style: 'modern',
              aspect_ratio: '1:1',
              quality: 'hd'
            }
          )
          
          if (aiResponse.success && aiResponse.image_url) {
            console.log('✅ NanoBanana generation successful')
            setGenerationStep('generating')
            
            const posterData = {
              url: aiResponse.image_url,
              captions: [
                `Discover our beautiful ${promptParams.fabric} collection`,
                `Perfect for ${promptParams.occasion} celebrations`,
                `Premium quality ${promptParams.style} design`
              ],
              hashtags: [
                `#${promptParams.fabric}`,
                `#${promptParams.occasion}`,
                `#${promptParams.style}`,
                '#textile',
                '#fashion'
              ],
              metadata: {
                prompt: enhancedPrompt,
                generated_at: new Date().toISOString(),
                ai_service: 'nanobanana',
                unique_id: `gen_${Date.now()}`
              }
            }
            
            setGeneratedPoster(posterData)
            setAiServiceStatus('available')
            showSuccess('✅ AI generation completed successfully!')
            return
          } else {
            console.warn('NanoBanana generation failed, using backend fallback')
          }
        } catch (error) {
          console.warn('NanoBanana API error, using backend fallback:', error)
        }
      } else {
        console.log('Using backend generation (NanoBanana not configured or failed)')
      }

      // Fallback to backend generation
      await handleGenerateWithBackend(enhancedPrompt)
      
    } catch (error) {
      console.error('Generation error:', error)
      setGenerationError('AI generation failed. Please try again.')
      setAiServiceStatus('error')
      showError('AI generation failed. Please try again.')
    } finally {
      setIsGenerating(false)
      setGenerationStep('idle')
    }
  }

  const handleGenerateWithBackend = async (enhancedPrompt: string) => {
    if (!uploadedFiles.length) {
      showError("Please upload at least one image")
      return
    }

    // Upload files first
    const uploadPromises = uploadedFiles.map(file => apiClient.uploadFile(file))
    const uploadResults = await Promise.all(uploadPromises)
    
    const successfulUploads = uploadResults.filter(result => result.success)
    if (successfulUploads.length === 0) {
      showError("Failed to upload files")
      return
    }
    
    const productImageUrl = successfulUploads[0].data!.url
    console.log('Files uploaded successfully:', successfulUploads.length)
    
    // Generate poster using backend workflow
    let result
    try {
      console.log('🚀 Calling backend AI generation')
      
      // Optional UI step indicators
      setGenerationStep('refining')
      
      result = await apiClient.generatePosterTwoStep({
        product_image_url: productImageUrl,
        fabric_type: 'silk',
        festival: 'general',
        price_range: '₹2999',
        style: 'modern',
        custom_text: enhancedPrompt,
        offer_details: 'Special offer available',
        color_palette: extractedColors.map(c => (c.name || c.hex || '').toLowerCase()).filter(Boolean),
        generation_type: 'poster'
      })
      
      // Optional UI step indicators
      setGenerationStep('generating')
      
      console.log('✅ Backend generation completed:', result)
    } catch (error) {
      console.warn('Backend generation failed:', error)
      setGenerationError('AI image generation is currently unavailable. Please try again later.')
      setAiServiceStatus('error')
      showError('AI image generation is currently unavailable. Please try again later.')
      return
    }
    
    if (!result.success) {
      console.warn('Backend generation failed:', result.error)
      setGenerationError('AI image generation is currently unavailable. Please try again later.')
      setAiServiceStatus('error')
      showError('AI image generation is currently unavailable. Please try again later.')
      return
    }
    
    const data = result.data!
    console.log('🔍 Backend response data:', data)
    console.log('🖼️ Poster URL from backend:', data.poster_url)
    
    // Check if the data indicates a fallback response
    if (data.success === false && data.error) {
      console.warn('Backend returned fallback response:', data.error)
      setGenerationError(data.error)
      setAiServiceStatus('error')
      showError(data.error)
      return
    }
    
    // Validate poster URL before setting poster data
    if (!data.poster_url || data.poster_url.trim() === '') {
      console.error('❌ No poster URL provided in response')
      setGenerationError('No image was generated. Please try again.')
      setAiServiceStatus('error')
      showError('No image was generated. Please try again.')
      return
    }
    
    // Additional URL validation - handle both relative and absolute URLs
    try {
      // If it's already an absolute URL, validate it
      if (data.poster_url.startsWith('http://') || data.poster_url.startsWith('https://')) {
        new URL(data.poster_url)
      }
      // If it's a relative URL, check if it starts with '/' (valid relative path)
      else if (!data.poster_url.startsWith('/')) {
        throw new Error('Invalid relative URL format')
      }
    } catch {
      console.error('❌ Invalid poster URL format:', data.poster_url)
      setGenerationError('Invalid image URL generated. Please try again.')
      setAiServiceStatus('error')
      showError('Invalid image URL generated. Please try again.')
      return
    }
    
    // Generate dynamic captions based on the prompt and selections
    const dynamicCaptions = [
      `Discover our beautiful silk collection`,
      `Perfect for general celebrations`,
      `Premium quality modern design`
    ]
    
    const dynamicHashtags = [
      '#silk',
      '#general',
      '#modern',
      '#textile',
      '#fashion'
    ]
    
    console.log('🎨 Setting generated poster with URL:', data.poster_url)
    console.log('📊 Full response data:', data)
    
    const posterData = {
      url: data.poster_url,
      captions: data.caption_suggestions?.length > 0 ? data.caption_suggestions : dynamicCaptions,
      hashtags: data.hashtags?.length > 0 ? data.hashtags : dynamicHashtags,
      metadata: {
        prompt: enhancedPrompt,
        generated_at: new Date().toISOString(),
        ai_service: 'backend',
        unique_id: (data.metadata as { unique_id?: string } | undefined)?.unique_id || `gen_${Date.now()}`
      }
    }
    
    console.log('📝 Generated poster data:', posterData)
    setGeneratedPoster(posterData)
    
    // Completion
    setGenerationStep('completed')
    setGenerationError(null)
    showSuccess('✅ AI generation completed successfully!')
    
    // Store refined prompt for display
    if (data.metadata?.refined_prompt) {
      setRefinedPrompt(data.metadata.refined_prompt)
    }
    
    setAiServiceStatus('available')
  }

  const handleDownload = async () => {
    if (!generatedPoster) {
      showError("No poster to download")
      return
    }
    
    setIsDownloading(true)
    try {
      const success = await apiClient.downloadFile(generatedPoster.url, `poster_${Date.now()}.png`)
      if (success) {
        showSuccess("Poster downloaded successfully!")
      } else {
        showError("Download failed")
      }
    } catch (error) {
      console.error("Download error:", error)
      showError("Download failed")
    } finally {
      setIsDownloading(false)
    }
  }

  const handleSchedule = () => {
    if (!generatedPoster) {
      showError("No poster to schedule")
      return
    }
    
    setScheduleData(prev => ({
      ...prev,
      caption: generatedPoster.captions[0] || "Check out our latest collection!"
    }))
    setShowScheduleModal(true)
  }

  const handlePostToSocial = async () => {
    if (!generatedPoster) {
      showError("No poster to post")
      return
    }
    
    setIsPosting(true)
    try {
      const result = await apiClient.postToSocialMedia({
        platform: 'instagram',
        asset_url: generatedPoster.url,
        caption: generatedPoster.captions[0] || "Check out our latest collection!",
        metadata: {
          hashtags: generatedPoster.hashtags,
          generated_at: generatedPoster.metadata?.generated_at
        }
      })
      
      if (result.success) {
        showSuccess("Posted to social media successfully!")
      } else {
        showError(result.error || "Failed to post to social media")
      }
    } catch (error) {
      console.error("Social media posting error:", error)
      showError("Failed to post to social media")
    } finally {
      setIsPosting(false)
    }
  }

  // Enhanced image error handler
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    console.error('❌ Image failed to load:', e)
    console.error('❌ Image URL:', generatedPoster?.url)
    console.error('❌ Full poster data:', generatedPoster)
    
    setImageLoadError(true)
    setGenerationError('Failed to load generated image. The image URL may be invalid or the file may not exist.')
    setAiServiceStatus('error')
    showError('Failed to load generated image. Please try generating again.')
  }

  const handleImageLoad = () => {
    console.log('✅ Image loaded successfully')
    setImageLoadError(false)
    setGenerationError(null)
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Input */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="h-5 w-5" />
                AI Poster Generator
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="prompt">Product Description</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe your textile product... (e.g., 'Beautiful silk saree for festive occasions')"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>

              <div>
                <Label>Upload Product Images</Label>
                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center">
                  <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drag and drop images here, or click to select
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Choose Files
                  </Button>
                </div>
                
                {uploadedFiles.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">{file.name}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <ColorPaletteExtractor
                onPaletteExtracted={setExtractedColors}
              />

              <div className="flex gap-2">
                <Button
                  onClick={handleGenerateWithAI}
                  disabled={isGenerating || !prompt.trim()}
                  className="flex-1"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Wand2 className="mr-2 h-4 w-4" />
                      Generate Poster
                    </>
                  )}
                </Button>
              </div>

              {generationStep !== 'idle' && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    {generationStep === 'refining' && (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Refining prompt...
                      </>
                    )}
                    {generationStep === 'generating' && (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Generating image...
                      </>
                    )}
                    {generationStep === 'completed' && (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Generation completed!
                      </>
                    )}
                  </div>
                </div>
              )}

              {generationError && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700">{generationError}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Output */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Generated Poster
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-muted rounded-lg flex items-center justify-center mb-4 overflow-hidden relative w-full" style={{ aspectRatio: '4 / 5' }}>
              {generatedPoster && !imageLoadError ? (
                  <>
                    {console.log('🖼️ Rendering image with URL:', generatedPoster.url)}
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={generatedPoster.url}
                      alt="AI Generated poster"
                      className="absolute inset-0 w-full h-full object-contain rounded-lg"
                      onLoad={handleImageLoad}
                      onError={handleImageError}
                    />
                  </>
                ) : (
                  <div className="text-center">
                    <Sparkles className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      {generationError || 'AI-generated poster will appear here'}
                    </p>
                    {imageLoadError && (
                      <p className="text-red-500 text-sm mt-2">
                        Image failed to load. Please try generating again.
                      </p>
                    )}
                  </div>
                )}
              </div>

              {generatedPoster && !imageLoadError && (
                <div className="space-y-4">
                  <div>
                    <Label>Captions</Label>
                    <div className="space-y-2">
                      {generatedPoster.captions.map((caption, index) => (
                        <div key={index} className="p-2 bg-muted rounded text-sm">
                          {caption}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label>Hashtags</Label>
                    <div className="flex flex-wrap gap-1">
                      {generatedPoster.hashtags.map((hashtag, index) => (
                        <Badge key={index} variant="secondary">
                          {hashtag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={handleDownload}
                      disabled={isDownloading}
                      variant="outline"
                      className="flex-1"
                    >
                      {isDownloading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Download className="mr-2 h-4 w-4" />
                      )}
                      Download
                    </Button>
                    <Button
                      onClick={handleSchedule}
                      variant="outline"
                      className="flex-1"
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      Schedule
                    </Button>
                    <Button
                      onClick={handlePostToSocial}
                      disabled={isPosting}
                      className="flex-1"
                    >
                      {isPosting ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Share2 className="mr-2 h-4 w-4" />
                      )}
                      Post
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

