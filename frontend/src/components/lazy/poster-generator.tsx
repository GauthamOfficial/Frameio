"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Upload, Wand2, Calendar, Share2, Download, X } from "lucide-react"
import React, { useState, useRef } from "react"
import { useToastHelpers } from "@/components/common"
import { useAppContext } from "@/contexts/app-context"
import { apiClient } from "@/lib/api-client"

export default function PosterGenerator() {
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
  
  const [isGenerating, setIsGenerating] = useState(false)
  const [isScheduling, setIsScheduling] = useState(false)
  const [isPosting, setIsPosting] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [selectedStyle, setSelectedStyle] = useState("")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [generatedPoster, setGeneratedPoster] = useState<{
    url: string
    captions: string[]
    hashtags: string[]
  } | null>(null)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [scheduleData, setScheduleData] = useState({
    platform: 'instagram',
    scheduledTime: '',
    caption: ''
  })

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
    const result = await apiClient.uploadFile(file)
    if (!result.success) {
      throw new Error(result.error || 'Failed to upload file')
    }
    return result.data!.url
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      showError("Please enter a prompt for the poster generation")
      return
    }
    
    if (uploadedFiles.length === 0) {
      showError("Please upload at least one image")
      return
    }

    setIsGenerating(true)
    try {
      // Upload files first
      const uploadedUrls = await Promise.all(
        uploadedFiles.map(file => uploadFileToServer(file))
      )
      
      // Generate poster using AI service
      const result = await apiClient.generatePoster({
        product_image_url: uploadedUrls[0], // Use first image
        fabric_type: 'silk', // Default, could be made configurable
        festival: 'general',
        price_range: '₹2999',
        style: selectedStyle || 'modern',
        custom_text: prompt,
        offer_details: 'Special offer available'
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to generate poster')
      }
      
      const data = result.data!
      setGeneratedPoster({
        url: data.poster_url,
        captions: data.caption_suggestions || [],
        hashtags: data.hashtags || []
      })
      
      showSuccess("Poster generated successfully!")
    } catch (error) {
      showError(`Failed to generate poster: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
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
        `poster-${Date.now()}.png`
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
          generated_at: new Date().toISOString()
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
        caption: generatedPoster.captions[0] || 'Check out this amazing textile design!',
        metadata: {
          hashtags: generatedPoster.hashtags
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

  const styles = [
    { id: "festival", label: "Festival" },
    { id: "modern", label: "Modern" },
    { id: "traditional", label: "Traditional" },
    { id: "minimalist", label: "Minimalist" },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Poster Generator</h1>
          <p className="text-muted-foreground mt-1">
            Create stunning textile marketing posters with AI assistance.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Upload & Configure</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div className="space-y-2">
              <Label htmlFor="upload">Upload Images</Label>
              <div 
                className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-sm text-muted-foreground mb-2">
                  Drag and drop your textile images here, or click to browse
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
                          <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
                            <Upload className="h-4 w-4 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">{file.name}</p>
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
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Prompt Input */}
            <div className="space-y-2">
              <Label htmlFor="prompt">AI Prompt</Label>
              <Textarea
                id="prompt"
                placeholder="Describe the style, colors, and mood for your poster..."
                className="min-h-[100px]"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            {/* Style Options */}
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

            {/* Generate Button */}
            <Button 
              className="w-full bg-textile-accent"
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              <Wand2 className="mr-2 h-4 w-4" />
              {isGenerating ? "Generating..." : "Generate Poster"}
            </Button>
          </CardContent>
        </Card>

        {/* Preview Section */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-[4/5] bg-muted rounded-lg flex items-center justify-center mb-4 overflow-hidden">
              {generatedPoster ? (
                <img
                  src={generatedPoster.url}
                  alt="Generated poster"
                  className="w-full h-full object-cover rounded-lg"
                />
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Generated poster will appear here</p>
                </div>
              )}
            </div>
            
            {/* Generated Content Info */}
            {generatedPoster && (
              <div className="space-y-3 mb-4">
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

      {/* Recent Generations */}
      <Card className="textile-hover textile-shadow">
        <CardHeader>
          <CardTitle>Recent Generations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
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
                  onChange={(e) => setScheduleData(prev => ({ ...prev, platform: e.target.value }))}
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
