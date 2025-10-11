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
  Type,
  Image as ImageIcon
} from "lucide-react"
import React, { useState, useRef } from "react"

interface GenerationResult {
  success: boolean
  message?: string
  image_path?: string
  image_url?: string
  filename?: string
  error?: string
  text_added?: string
  style?: string
}

export default function EnhancedPosterGenerator() {
  // State management
  const [isGenerating, setIsGenerating] = useState(false)
  const [prompt, setPrompt] = useState("")
  const [aspectRatio, setAspectRatio] = useState("4:5")
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Text overlay functionality
  const [mode, setMode] = useState<'generate' | 'text-overlay'>('generate')
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [textPrompt, setTextPrompt] = useState("")
  const [textStyle, setTextStyle] = useState("elegant")
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

      const response = await fetch('http://localhost:8000/api/ai/ai-poster/generate_poster/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          aspect_ratio: aspectRatio
        })
      })

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

  const addTextOverlay = async () => {
    if (!uploadedImage || !textPrompt.trim()) {
      setError('Please upload an image and enter text to add')
      return
    }

    setIsGenerating(true)
    setError(null)
    setResult(null)

    try {
      console.log('🚀 Starting text overlay...')
      console.log('Text prompt:', textPrompt)
      console.log('Text style:', textStyle)

      const formData = new FormData()
      formData.append('image', uploadedImage)
      formData.append('text_prompt', textPrompt)
      formData.append('text_style', textStyle)

      const response = await fetch('http://localhost:8000/api/ai/ai-poster/add_text_overlay/', {
        method: 'POST',
        body: formData
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('Text overlay result:', data)

      if (data.success) {
        setResult(data)
        setError(null)
        console.log('✅ Text overlay added successfully!')
        console.log('Image URL:', data.image_url)
      } else {
        throw new Error(data.error || 'Text overlay failed')
      }
    } catch (err) {
      console.error('❌ Text overlay failed:', err)
      setError(err instanceof Error ? err.message : 'Text overlay failed')
      setResult(null)
    } finally {
      setIsGenerating(false)
    }
  }

  const resetTextOverlay = () => {
    setUploadedImage(null)
    setTextPrompt("")
    setTextStyle("elegant")
    setPreviewUrl(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">AI Poster Generator</h1>
        <p className="text-center text-gray-600">Generate beautiful textile posters or add text to existing images using Gemini 2.5 Flash</p>
        
        {/* Mode Selection */}
        <div className="flex justify-center mt-6">
          <div className="bg-gray-100 rounded-lg p-1 flex">
            <button
              onClick={() => setMode('generate')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === 'generate'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Wand2 className="w-4 h-4 inline mr-2" />
              Generate Poster
            </button>
            <button
              onClick={() => setMode('text-overlay')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === 'text-overlay'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Type className="w-4 h-4 inline mr-2" />
              Add Text to Image
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>{mode === 'generate' ? 'Generate Poster' : 'Add Text to Image'}</span>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {mode === 'generate' ? (
              <>
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
                      Generating...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Generate Poster
                    </>
                  )}
                </Button>
              </>
            ) : (
              <>
                <div>
                  <Label htmlFor="image-upload">Upload Textile Image</Label>
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
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isGenerating}
                      className="w-full"
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      {uploadedImage ? 'Change Image' : 'Choose Image'}
                    </Button>
                  </div>
                  {uploadedImage && (
                    <p className="text-sm text-gray-600 mt-2">
                      Selected: {uploadedImage.name}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="text-prompt">Text to Add</Label>
                  <Input
                    id="text-prompt"
                    placeholder="e.g., Premium Silk Collection"
                    value={textPrompt}
                    onChange={(e) => setTextPrompt(e.target.value)}
                    disabled={isGenerating}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="text-style">Text Style</Label>
                  <select
                    id="text-style"
                    value={textStyle}
                    onChange={(e) => setTextStyle(e.target.value)}
                    disabled={isGenerating}
                    className="mt-1 w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="elegant">Elegant</option>
                    <option value="bold">Bold</option>
                    <option value="modern">Modern</option>
                    <option value="vintage">Vintage</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={addTextOverlay} 
                    disabled={isGenerating || !uploadedImage || !textPrompt.trim()}
                    className="flex-1"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Adding Text...
                      </>
                    ) : (
                      <>
                        <Type className="mr-2 h-4 w-4" />
                        Add Text
                      </>
                    )}
                  </Button>
                  <Button 
                    onClick={resetTextOverlay} 
                    disabled={isGenerating}
                    variant="outline"
                  >
                    Reset
                  </Button>
                </div>
              </>
            )}

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
              {mode === 'generate' ? 'Generated Poster' : 'Text Overlay Result'}
              {result?.success && <CheckCircle className="h-4 w-4 text-green-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-4" />
                <p className="text-gray-600">
                  {mode === 'generate' ? 'Generating your poster...' : 'Adding text to your image...'}
                </p>
                <p className="text-sm text-gray-500 mt-2">This may take 60-120 seconds</p>
              </div>
            )}

            {result?.success && result.image_url && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={result.image_url.startsWith('http') ? result.image_url : `http://localhost:8000${result.image_url}`}
                    alt={mode === 'generate' ? 'Generated poster' : 'Image with text overlay'}
                    className="w-full h-auto rounded-md border"
                    onError={(e) => {
                      console.error('Image load error:', e)
                      console.error('Image URL:', result.image_url)
                      setError('Failed to load generated image. Please try again.')
                    }}
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Filename:</span>
                    <span className="font-mono">{result.filename}</span>
                  </div>
                  
                  {result.text_added && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <span>Text added:</span>
                      <span className="font-medium">{result.text_added}</span>
                    </div>
                  )}
                  
                  {result.style && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <span>Style:</span>
                      <span className="font-medium capitalize">{result.style}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Path:</span>
                    <span className="font-mono text-xs break-all">{result.image_path}</span>
                  </div>
                </div>

                <Button onClick={downloadImage} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Image
                </Button>
              </div>
            )}

            {!isGenerating && !result && (
              <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                <div className="text-center">
                  <div className="text-4xl mb-4">
                    {mode === 'generate' ? '🎨' : '📝'}
                  </div>
                  <p className="text-gray-600">
                    {mode === 'generate' 
                      ? 'Your generated poster will appear here' 
                      : 'Your image with text overlay will appear here'
                    }
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    {mode === 'generate' 
                      ? 'Enter a prompt and click Generate Poster' 
                      : 'Upload an image, add text, and click Add Text'
                    }
                  </p>
                </div>
              </div>
            )}

            {/* Preview uploaded image in text overlay mode */}
            {mode === 'text-overlay' && previewUrl && !result && !isGenerating && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={previewUrl}
                    alt="Uploaded textile image"
                    className="w-full h-auto rounded-md border"
                  />
                </div>
                <p className="text-sm text-gray-600 text-center">
                  Uploaded image preview - Add text to process
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  )
}