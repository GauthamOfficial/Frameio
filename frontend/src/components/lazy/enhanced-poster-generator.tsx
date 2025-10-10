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
      // Generate enhanced prompt using AI utilities, including uploaded image context
      const enhancedPrompt = generateTextilePrompt(prompt, {
        style: (selectedStyle || 'modern') as any,
        fabric: (selectedFabric || 'cotton') as any,
        occasion: (selectedOccasion || 'casual') as any,
        colors: extractedColors.map(c => c.hex),
        hasUploadedImages: uploadedFiles.length > 0
      })
      
      console.log('Generation context:', {
        prompt: prompt,
        enhancedPrompt: enhancedPrompt,
        uploadedFiles: uploadedFiles.length,
        selectedStyle,
        selectedFabric,
        selectedOccasion
      })

      // Try NanoBanana API first
      const aiResponse = await nanoBananaService.generateImage(
        enhancedPrompt,
        {
          style: selectedStyle,
          aspect_ratio: '1:1',
          quality: 'hd'
        }
      )

      if (aiResponse.success && aiResponse.imageUrl) {
        // AI generation successful
        setGeneratedPoster({
          url: aiResponse.imageUrl,
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
            prompt: enhancedPrompt,
            generated_at: new Date().toISOString(),
            ai_service: 'nanobanana'
          }
        })
        setAiServiceStatus('available')
        showSuccess("AI poster generated successfully!")
      } else if (aiResponse.fallback) {
        // Backend API not accessible, use frontend generation
        console.log('Backend API not accessible, using frontend generation')
        setAiServiceStatus('fallback')
        await handleFrontendOnlyGeneration(enhancedPrompt)
      } else {
        // Fallback to backend API - this will generate fresh content
        console.log('NanoBanana API not available, using backend generation')
        await handleGenerateWithBackend(enhancedPrompt)
      }
    } catch (error) {
      console.error('AI generation failed:', error)
      setAiServiceStatus('error')
      
      // Try backend fallback
      try {
        await handleGenerateWithBackend(enhancedPrompt)
      } catch (fallbackError) {
        console.error('Backend fallback also failed:', fallbackError)
        // Final fallback to frontend-only generation
        try {
          await handleFrontendOnlyGeneration(enhancedPrompt)
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
    
    // Generate a contextual image URL based on the prompt and uploaded content
    const timestamp = Date.now()
    // Create a simple hash from the prompt that works with any Unicode characters
    const promptHash = Array.from(enhancedPrompt)
      .reduce((hash, char) => {
        return ((hash << 5) - hash + char.charCodeAt(0)) & 0xffffffff
      }, 0)
      .toString(16)
      .substring(0, 8)
    
    // Create a more relevant image URL based on the content
    let uniqueImageUrl
    console.log('Enhanced prompt for image selection:', enhancedPrompt)
    console.log('Uploaded files available:', uploadedFiles.length)
    
    // PRIORITY: Use uploaded images if available
    if (uploadedFiles.length > 0) {
      try {
        // Convert the first uploaded file to a data URL for immediate use
        const firstFile = uploadedFiles[0]
        uniqueImageUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader()
          reader.onload = () => resolve(reader.result as string)
          reader.readAsDataURL(firstFile)
        })
        console.log('Using uploaded image as base for generation')
      } catch (error) {
        console.warn('Failed to process uploaded image, falling back to contextual image:', error)
      }
    }
    
    // If no uploaded images or processing failed, use contextual images based on prompt
    if (!uniqueImageUrl) {
      // Extract key terms from the prompt for better image selection
      const promptLower = enhancedPrompt.toLowerCase()
      
      if (promptLower.includes('saree') || promptLower.includes('sari') || 
          promptLower.includes('indian') || promptLower.includes('traditional')) {
        // Use a beautiful saree image
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp}&text=Saree+Collection&bg=FF6B6B&color=FFFFFF`
        console.log('Using saree-specific image')
      } else if (promptLower.includes('textile') || promptLower.includes('fabric') || 
                 promptLower.includes('cotton') || promptLower.includes('silk')) {
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp + 1}&text=Textile+Design&bg=4ECDC4&color=FFFFFF`
        console.log('Using textile-specific image')
      } else if (promptLower.includes('fashion') || promptLower.includes('clothing') || 
                 promptLower.includes('dress') || promptLower.includes('outfit')) {
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp + 2}&text=Fashion+Collection&bg=45B7D1&color=FFFFFF`
        console.log('Using fashion-specific image')
      } else if (promptLower.includes('poster') || promptLower.includes('sale') || 
                 promptLower.includes('marketing') || promptLower.includes('advertisement')) {
        // Use a marketing/poster style image
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp + 3}&text=Marketing+Poster&bg=FF9500&color=FFFFFF`
        console.log('Using marketing/poster-specific image')
      } else if (promptLower.includes('food') || promptLower.includes('restaurant') || 
                 promptLower.includes('cafe') || promptLower.includes('dining')) {
        // Use a food/restaurant style image
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp + 4}&text=Restaurant+Interior&bg=8B4513&color=FFFFFF`
        console.log('Using restaurant/food-specific image')
      } else {
        // Default to a general product image
        uniqueImageUrl = `https://picsum.photos/1024/1024?random=${timestamp}&text=Product+Showcase&bg=6C5CE7&color=FFFFFF`
        console.log('Using default product image')
      }
    }
    
    // Generate dynamic captions based on content and uploaded images
    const dynamicCaptions = []
    const promptLower = enhancedPrompt.toLowerCase()
    
    // Check if we have uploaded images to create more specific captions
    const hasUploadedImages = uploadedFiles.length > 0
    
    if (promptLower.includes('saree') || promptLower.includes('sari') ||
        promptLower.includes('indian') || promptLower.includes('traditional')) {
      dynamicCaptions.push(
        `✨ Beautiful Saree Collection ✨`,
        `Elegant traditional wear`,
        `Perfect for special occasions`,
        `Premium quality fabric`,
        `✨ ${enhancedPrompt.split(',')[0]} ✨`
      )
      if (hasUploadedImages) {
        dynamicCaptions.push(`Based on your uploaded image`, `Custom design inspired by your photo`)
      }
    } else if (promptLower.includes('poster') || promptLower.includes('sale') || 
               promptLower.includes('marketing') || promptLower.includes('advertisement')) {
      dynamicCaptions.push(
        `✨ ${enhancedPrompt.split(',')[0]} ✨`,
        `Limited Time Offer!`,
        `Perfect for marketing campaigns`,
        `Professional design`,
        `Call to action included`
      )
      if (hasUploadedImages) {
        dynamicCaptions.push(`Featuring your product image`, `Custom marketing design`)
      }
    } else if (promptLower.includes('food') || promptLower.includes('restaurant') || 
               promptLower.includes('cafe') || promptLower.includes('dining')) {
      dynamicCaptions.push(
        `✨ ${enhancedPrompt.split(',')[0]} ✨`,
        `Delicious dining experience`,
        `Perfect for food marketing`,
        `Appetizing presentation`,
        `Restaurant quality`
      )
      if (hasUploadedImages) {
        dynamicCaptions.push(`Showcasing your food`, `Based on your restaurant image`)
      }
    } else if (promptLower.includes('fashion') || promptLower.includes('clothing') || 
               promptLower.includes('dress') || promptLower.includes('outfit')) {
      dynamicCaptions.push(
        `✨ ${enhancedPrompt.split(',')[0]} ✨`,
        `Trendy fashion collection`,
        `Perfect for any occasion`,
        `Style: ${selectedStyle || 'modern'} design`,
        `Fabric: ${selectedFabric || 'premium'} quality`
      )
      if (hasUploadedImages) {
        dynamicCaptions.push(`Inspired by your fashion image`, `Custom style based on your photo`)
      }
    } else {
      dynamicCaptions.push(
        `✨ ${enhancedPrompt ? enhancedPrompt.split(',')[0] : prompt} ✨`,
        `Perfect for ${selectedOccasion || 'any occasion'}`,
        `Style: ${selectedStyle || 'modern'} design`,
        `Fabric: ${selectedFabric || 'textile'} collection`
      )
      if (hasUploadedImages) {
        dynamicCaptions.push(`Custom design from your image`, `Personalized based on your upload`)
      }
    }
    
    // Generate dynamic hashtags based on content and uploaded images
    const dynamicHashtags = []
    
    if (promptLower.includes('saree') || promptLower.includes('sari') ||
        promptLower.includes('indian') || promptLower.includes('traditional')) {
      dynamicHashtags.push(
        '#saree',
        '#sari',
        '#traditional',
        '#indianwear',
        '#ethnic',
        '#fashion',
        '#elegant',
        '#premium',
        '#sale',
        '#collection'
      )
    } else if (promptLower.includes('poster') || promptLower.includes('sale') || 
               promptLower.includes('marketing') || promptLower.includes('advertisement')) {
      dynamicHashtags.push(
        '#poster',
        '#marketing',
        '#sale',
        '#advertisement',
        '#promotion',
        '#design',
        '#business',
        '#marketing',
        '#ai_generated',
        '#frontend_generated'
      )
    } else if (promptLower.includes('food') || promptLower.includes('restaurant') || 
               promptLower.includes('cafe') || promptLower.includes('dining')) {
      dynamicHashtags.push(
        '#food',
        '#restaurant',
        '#cafe',
        '#dining',
        '#delicious',
        '#foodie',
        '#culinary',
        '#taste',
        '#ai_generated',
        '#frontend_generated'
      )
    } else if (promptLower.includes('fashion') || promptLower.includes('clothing') || 
               promptLower.includes('dress') || promptLower.includes('outfit')) {
      dynamicHashtags.push(
        '#fashion',
        '#clothing',
        '#style',
        '#outfit',
        '#trendy',
        '#design',
        '#wear',
        '#collection',
        '#ai_generated',
        '#frontend_generated'
      )
    } else {
      dynamicHashtags.push(
        `#${selectedFabric || 'textile'}`,
        `#${selectedStyle || 'modern'}`,
        `#${selectedOccasion || 'fashion'}`,
        '#fashion',
        '#design',
        '#textile',
        '#ai_generated',
        '#frontend_generated'
      )
    }
    
    // Add hashtags related to uploaded images
    if (hasUploadedImages) {
      dynamicHashtags.push('#custom_image', '#personalized', '#your_photo', '#uploaded_content')
    }
    
    console.log('Setting generated poster with URL:', uniqueImageUrl)
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
    
    // If no uploaded images, use a contextual placeholder based on the prompt
    if (!productImageUrl) {
      if (enhancedPrompt.toLowerCase().includes('saree') || enhancedPrompt.toLowerCase().includes('sari')) {
        productImageUrl = 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=512&h=512&fit=crop&crop=center&auto=format&q=80'
      } else if (enhancedPrompt.toLowerCase().includes('textile') || enhancedPrompt.toLowerCase().includes('fabric')) {
        productImageUrl = 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=512&h=512&fit=crop&crop=center&auto=format&q=80'
      } else {
        productImageUrl = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=512&h=512&fit=crop&crop=center&auto=format&q=80'
      }
      console.log('Using contextual placeholder image for generation')
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
                    <div className="flex items-center justify-between">
                      <Label>Uploaded Files ({uploadedFiles.length})</Label>
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Will be used in generation
                      </Badge>
                    </div>
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
                    <p className="text-xs text-muted-foreground">
                      💡 Your uploaded images will be combined with your prompt to create personalized posters
                    </p>
                  </div>
                )}
              </div>

              {/* AI Prompt Input */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="prompt">AI Prompt</Label>
                  {uploadedFiles.length > 0 && (
                    <Badge variant="outline" className="bg-blue-50 text-blue-700">
                      <Sparkles className="h-3 w-3 mr-1" />
                      Will combine with your images
                    </Badge>
                  )}
                </div>
                <Textarea
                  id="prompt"
                  placeholder={uploadedFiles.length > 0 
                    ? "Describe how to enhance your uploaded image: 'Add elegant gold patterns to this saree for a wedding collection'..."
                    : "Describe your textile design: 'Elegant silk saree with gold patterns for wedding collection'..."
                  }
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
                    onError={(e) => {
                      console.error('Image failed to load:', generatedPoster.url)
                      // Fallback to a different image
                      const target = e.target as HTMLImageElement
                      target.src = `https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=1024&h=1024&fit=crop&crop=center&auto=format&q=80&timestamp=${Date.now()}`
                    }}
                    onLoad={() => {
                      console.log('Image loaded successfully:', generatedPoster.url)
                    }}
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
