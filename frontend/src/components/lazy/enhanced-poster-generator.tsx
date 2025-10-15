"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { 
  Wand2, 
  Download, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2,
  Upload,
  Copy,
  Hash,
  MessageSquare,
  Sparkles
} from "lucide-react"
import React, { useState, useRef } from "react"
import { useUser, useAuth } from '@clerk/nextjs'

interface GenerationResult {
  success: boolean
  message?: string
  image_path?: string
  image_url?: string
  filename?: string
  error?: string
  text_added?: string
  style?: string
  caption?: string
  full_caption?: string
  hashtags?: string[]
  emoji?: string
  call_to_action?: string
}

export default function EnhancedPosterGenerator() {
  // Authentication
  const { user } = useUser()
  const { getToken } = useAuth()
  
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [aspectRatio, setAspectRatio] = useState("4:5")
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Image upload functionality
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Caption and hashtag functionality
  const [showCaption, setShowCaption] = useState(false)
  const [copiedItem, setCopiedItem] = useState<string | null>(null)

  const generatePoster = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setIsGenerating(true)
    setError(null)
    setResult(null)

    try {
      console.log('🚀 Starting poster generation...')
      console.log('Prompt:', prompt)
      console.log('Aspect Ratio:', aspectRatio)
      console.log('Has uploaded image:', !!uploadedImage)
      console.log('User authenticated:', !!user)

      // Get authentication token
      const token = await getToken()
      const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {}

      let response;

      if (uploadedImage) {
        // Generate poster with uploaded image
        const formData = new FormData()
        formData.append('image', uploadedImage)
        formData.append('prompt', prompt)
        formData.append('aspect_ratio', aspectRatio)

        response = await fetch('http://localhost:8000/api/ai/ai-poster/edit_poster/', {
          method: 'POST',
          headers: authHeaders,
          body: formData
        })
      } else {
        // Generate poster from text only
        response = await fetch('http://localhost:8000/api/ai/ai-poster/generate_poster/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify({
            prompt: prompt,
            aspect_ratio: aspectRatio
          })
        })
      }

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('Generation result:', data)

      if (data.success) {
        setResult(data)
        setError(null)
        console.log('✅ Poster generated successfully!')
        console.log('Image URL:', data.image_url)
        console.log('Image Path:', data.image_path)
        console.log('Full Image URL:', data.image_url.startsWith('http') ? data.image_url : `http://localhost:8000${data.image_url}`)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      console.error('❌ Generation failed:', err)
      setError(err instanceof Error ? err.message : 'Generation failed')
      setResult(null)
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadImage = async () => {
    if (result?.image_url) {
      try {
        // The backend now provides full URLs, but keep fallback for safety
        const downloadUrl = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        
        // Fetch the image as a blob to force download
        const response = await fetch(downloadUrl)
        const blob = await response.blob()
        
        // Create a blob URL and download
        const blobUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = blobUrl
        link.download = result.filename || 'generated-poster.png'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(blobUrl)
      } catch (error) {
        console.error('Download failed:', error)
        // Fallback to direct link
        const link = document.createElement('a')
        link.href = result.image_url.startsWith('http') 
          ? result.image_url 
          : `http://localhost:8000${result.image_url}`
        link.download = result.filename || 'generated-poster.png'
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedImage(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setError(null)
    }
  }

  const clearUploadedImage = () => {
    setUploadedImage(null)
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const copyHashtags = async () => {
    if (result?.hashtags) {
      const hashtagText = result.hashtags.join(' ')
      await copyToClipboard(hashtagText, 'hashtags')
    }
  }

  const copyFullCaption = async () => {
    if (result?.full_caption) {
      await copyToClipboard(result.full_caption, 'caption')
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generator</h1>
        <p className="text-center text-gray-600">Generate beautiful textile posters from text prompts or upload an image to create posters based on your textile designs using Gemini 2.5 Flash</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>Generate Poster</span>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="prompt">Describe your poster</Label>
              <Input
                id="prompt"
                placeholder="e.g., Beautiful silk saree for Diwali celebrations with gold accents"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isGenerating}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="image-upload">Upload Reference Image (Optional)</Label>
              <div className="mt-1">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isGenerating}
                  className="hidden"
                  id="image-upload"
                />
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isGenerating}
                    className="flex-1"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    {uploadedImage ? 'Change Image' : 'Choose Image'}
                  </Button>
                  {uploadedImage && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={clearUploadedImage}
                      disabled={isGenerating}
                    >
                      Clear
                    </Button>
                  )}
                </div>
                {uploadedImage && (
                  <p className="text-sm text-gray-600 mt-2">
                    Selected: {uploadedImage.name}
                  </p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="aspect-ratio">Aspect Ratio</Label>
              <select
                id="aspect-ratio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                disabled={isGenerating}
                className="mt-1 w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="1:1">Square (1:1)</option>
                <option value="4:5">Portrait (4:5)</option>
                <option value="16:9">Widescreen (16:9)</option>
              </select>
            </div>

            <Button 
              onClick={generatePoster} 
              disabled={isGenerating || !prompt.trim()}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {uploadedImage ? 'Generating from Image...' : 'Generating...'}
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  {uploadedImage ? 'Generate from Image' : 'Generate Poster'}
                </>
              )}
            </Button>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Generated Poster
              {result?.success && <CheckCircle className="h-4 w-4 text-green-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-600">Generating your poster...</p>
                <p className="text-sm text-gray-500 mt-2">This may take 60-120 seconds</p>
              </div>
            )}

            {result?.success && result.image_url && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={result.image_url.startsWith('http') ? result.image_url : `http://localhost:8000${result.image_url}`}
                    alt="Generated poster"
                    className="w-full h-auto rounded-md border"
                    onError={(e) => {
                      console.error('Image load error:', e)
                      console.error('Image URL:', result.image_url)
                      setError('Failed to load generated image. Please try again.')
                    }}
                  />
                </div>
                

                <Button onClick={downloadImage} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Image
                </Button>

                {/* Caption and Hashtags Section */}
                {(result.caption || result.hashtags) && (
                  <div className="mt-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-500" />
                        AI Generated Content
                      </h3>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowCaption(!showCaption)}
                      >
                        {showCaption ? 'Hide' : 'Show'} Content
                      </Button>
                    </div>

                    {showCaption && (
                      <div className="space-y-4">
                        {/* Caption Section */}
                        {result.caption && (
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <MessageSquare className="h-4 w-4" />
                                Caption
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-700 mb-3">{result.caption}</p>
                              {result.full_caption && (
                                <div className="space-y-2">
                                  <p className="text-xs text-gray-500">Full Caption:</p>
                                  <div className="bg-gray-50 p-3 rounded-md">
                                    <p className="text-sm">{result.full_caption}</p>
                                  </div>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={copyFullCaption}
                                    className="w-full"
                                  >
                                    <Copy className="mr-2 h-3 w-3" />
                                    {copiedItem === 'caption' ? 'Copied!' : 'Copy Full Caption'}
                                  </Button>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}

                        {/* Hashtags Section */}
                        {result.hashtags && result.hashtags.length > 0 && (
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <Hash className="h-4 w-4" />
                                Hashtags ({result.hashtags.length})
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <div className="flex flex-wrap gap-2 mb-3">
                                {result.hashtags.map((hashtag, index) => (
                                  <span
                                    key={index}
                                    className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs"
                                  >
                                    {hashtag}
                                  </span>
                                ))}
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={copyHashtags}
                                className="w-full"
                              >
                                <Copy className="mr-2 h-3 w-3" />
                                {copiedItem === 'hashtags' ? 'Copied!' : 'Copy All Hashtags'}
                              </Button>
                            </CardContent>
                          </Card>
                        )}

                        {/* Call to Action */}
                        {result.call_to_action && (
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm">Call to Action</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0">
                              <p className="text-sm text-gray-700">{result.call_to_action}</p>
                            </CardContent>
                          </Card>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {!isGenerating && !result && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <div className="text-center">
                  <div className="text-4xl mb-4">🎨</div>
                  <p className="text-gray-600">Your generated poster will appear here</p>
                  <p className="text-sm text-gray-500 mt-2">Enter a prompt and click Generate Poster</p>
                </div>
              </div>
            )}

            {/* Preview uploaded image */}
            {previewUrl && !result && !isGenerating && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={previewUrl}
                    alt="Uploaded reference image"
                    className="w-full h-auto rounded-md border"
                  />
                </div>
                <p className="text-sm text-gray-600 text-center">
                  Reference image - Will be used to generate your poster
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  )
}