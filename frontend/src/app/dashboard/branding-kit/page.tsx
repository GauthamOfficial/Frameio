"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Wand2, Eye, Download, RefreshCw } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { apiPost } from "@/utils/api"

interface BrandingKitData {
  logo?: {
    data: string
    format: string
    width: number
    height: number
  }
  color_palette?: {
    data: string
    format: string
    width: number
    height: number
  }
}

export default function BrandingKitPage() {
  const [prompt, setPrompt] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [brandingData, setBrandingData] = useState<BrandingKitData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { getToken } = useAuth()
  
  // Textarea auto-resize functionality
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  // Auto-resize textarea based on content
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto'
      // Set height based on scrollHeight, with min and max constraints
      const newHeight = Math.min(Math.max(textarea.scrollHeight, 100), 500)
      textarea.style.height = `${newHeight}px`
    }
  }, [])
  
  // Adjust height when prompt changes
  useEffect(() => {
    adjustTextareaHeight()
  }, [prompt, adjustTextareaHeight])

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    
    setIsGenerating(true)
    setError(null)
    
    try {
      const token = await getToken()
      
      const result = await apiPost<{ success: boolean; data?: { branding_kit: BrandingKitData }; error?: string }>(
        '/api/ai/branding-kit/generate/',
        {
          prompt: prompt.trim(),
          style: 'modern'
        },
        undefined,
        token
      )
      
      if (result.success && result.data) {
        setBrandingData(result.data.branding_kit)
        // Trigger a custom event to refresh the dashboard history
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('branding-kit-generated'))
        }
      } else {
        setError(result.error || 'Failed to generate branding kit')
      }
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid response from server. Please check if the backend is running.')
      } else {
        setError(`Network error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`)
      }
      console.error('Error generating branding kit:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadImage = (base64Data: string, filename: string, format: string) => {
    try {
      // Create a blob from the base64 data
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: `image/${format.toLowerCase()}` })
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading image:', error)
      setError('Failed to download image')
    }
  }

  const createZipFile = async (logoData: string, paletteData: string, logoFormat: string, paletteFormat: string) => {
    try {
      // Import JSZip dynamically
      const JSZip = (await import('jszip')).default
      const zip = new JSZip()
      
      // Add logo to zip
      if (logoData) {
        const logoBytes = Uint8Array.from(atob(logoData), c => c.charCodeAt(0))
        zip.file(`logo.${logoFormat.toLowerCase()}`, logoBytes)
      }
      
      // Add color palette to zip
      if (paletteData) {
        const paletteBytes = Uint8Array.from(atob(paletteData), c => c.charCodeAt(0))
        zip.file(`color-palette.${paletteFormat.toLowerCase()}`, paletteBytes)
      }
      
      // Add a README file with branding information
      const readmeContent = `Branding Kit Generated
========================

Generated on: ${new Date().toLocaleString()}
Prompt: ${prompt}

Files included:
- logo.${logoFormat.toLowerCase()} - Your brand logo
- color-palette.${paletteFormat.toLowerCase()} - Your brand color palette

This branding kit was generated using AI and is ready for use in your marketing materials.
`
      zip.file('README.txt', readmeContent)
      
      // Generate the zip file
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      
      // Create download link
      const url = URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `branding-kit-${Date.now()}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Error creating zip file:', error)
      setError('Failed to create zip file. Please try downloading files individually.')
    }
  }

  const handleDownloadAll = async () => {
    if (!brandingData) return
    
    try {
      if (brandingData.logo && brandingData.color_palette) {
        await createZipFile(
          brandingData.logo.data,
          brandingData.color_palette.data,
          brandingData.logo.format,
          brandingData.color_palette.format
        )
      } else {
        // Fallback to individual downloads if zip creation fails
        if (brandingData.logo) {
          downloadImage(
            brandingData.logo.data,
            `logo-${Date.now()}.${brandingData.logo.format.toLowerCase()}`,
            brandingData.logo.format
          )
        }
        
        if (brandingData.color_palette) {
          downloadImage(
            brandingData.color_palette.data,
            `color-palette-${Date.now()}.${brandingData.color_palette.format.toLowerCase()}`,
            brandingData.color_palette.format
          )
        }
      }
    } catch (error) {
      console.error('Error downloading files:', error)
      setError('Failed to download files')
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6 md:space-y-8">
        {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground">AI Brand Kit Generator</h1>
        </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
        {/* Prompting Section */}
        <Card className="textile-hover textile-shadow">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl">
              Generate Brand Kit
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 sm:space-y-6 p-4 sm:p-6">
            <div className="space-y-2">
              <Label htmlFor="brand-prompt" className="text-sm sm:text-base">Describe your brand vision</Label>
              <Textarea
                ref={textareaRef}
                id="brand-prompt"
                placeholder="describe your logo idea"
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value)
                  // Auto-resize on input
                  setTimeout(() => adjustTextareaHeight(), 0)
                }}
                disabled={isGenerating}
                className="min-h-[100px] max-h-[500px] resize-none overflow-y-auto placeholder:opacity-50 text-sm sm:text-base"
                style={{ height: 'auto' }}
              />
            </div>

            {/* Templates Section */}
            <div className="space-y-2">
              <Label className="text-sm sm:text-base">Templates</Label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setPrompt("Create a professional and elegant logo for a fashion textile brand.\n\nBrand Name: [Your Company Name]\nColor Palette: [Choose your preferred colors]\nDesign Elements: [Specify main visual]\n\nThe logo should reflect a premium, modern, and stylish aesthetic suitable for a fashion and textile brand. Use smooth typography and minimalist detailing to make it versatile for social media, tags, and packaging.\n\nProvide the logo on a clean white or soft gradient background, centered and ready for branding use.")
                    setTimeout(() => adjustTextareaHeight(), 0)
                  }}
                  className="p-2 sm:p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-xs sm:text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-square rounded-md mb-1 sm:mb-2 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/Fashion Textile.png" 
                      alt="Fashion Textile" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700 text-xs sm:text-sm">Fashion Textiles</div>
                  <div className="text-gray-500 text-xs mt-1 hidden sm:block">Elegant & Luxury</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setPrompt("Create a playful yet professional logo for a kids' textile brand.\n\nBrand Name: [Your Company Name]\nColor Palette: [Choose your preferred bright or pastel colors]\nDesign Elements: [Specify main visuals]\n\nThe logo should reflect a cute, friendly, and premium aesthetic suitable for a children's clothing and textile brand. Use soft, rounded typography and minimal yet fun details to appeal to both kids and parents.\n\nProvide the logo on a clean white or soft gradient pastel background, centered and ready for branding use.")
                    setTimeout(() => adjustTextareaHeight(), 0)
                  }}
                  className="p-2 sm:p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-xs sm:text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-square rounded-md mb-1 sm:mb-2 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/Kids.png" 
                      alt="Kids Textile" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700 text-xs sm:text-sm">Kids Textiles</div>
                  <div className="text-gray-500 text-xs mt-1 hidden sm:block">Playful & Bright</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setPrompt("Create a bold and professional logo for a wholesale textile company.\n\nBrand Name: [Your Company Name]\nColor Palette: [Choose your preferred bright or pastel colors]\nDesign Elements: [Specify main visuals]\n\nThe logo should reflect trust, scale, and quality, representing a reliable wholesale textile business. Use clean typography, geometric balance, and minimal detailing to ensure it looks strong on signage, invoices, and packaging.\n\nProvide the logo on a white or light gradient professional background, centered and ready for branding use.")
                    setTimeout(() => adjustTextareaHeight(), 0)
                  }}
                  className="p-2 sm:p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-xs sm:text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-square rounded-md mb-1 sm:mb-2 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/wholesale.png" 
                      alt="Wholesale Textile" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700 text-xs sm:text-sm">Wholesale</div>
                  <div className="text-gray-500 text-xs mt-1 hidden sm:block">Professional</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setPrompt("Create a modern and professional logo for an online textile e-commerce platform.\n\nBrand Name: [Your Company Name]\nColor Palette: [Choose your preferred colors]\nDesign Elements: [Specify main visual]\n\nThe logo should reflect a premium, trustworthy, and digital-friendly aesthetic, representing an e-commerce textile platform. Use smooth, modern typography and minimalist detailing that looks perfect on a website, app icon, and social media.\n\nProvide the logo on a clean white or soft gradient background, centered and ready for digital branding use.")
                    setTimeout(() => adjustTextareaHeight(), 0)
                  }}
                  className="p-2 sm:p-3 text-center border border-gray-200 rounded-md hover:border-gray-300 hover:bg-gray-50 transition-colors text-xs sm:text-sm"
                  disabled={isGenerating}
                >
                  <div className="w-full aspect-square rounded-md mb-1 sm:mb-2 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src="/Online.png" 
                      alt="Online Textile" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="font-medium text-gray-700 text-xs sm:text-sm">Online Textiles</div>
                  <div className="text-gray-500 text-xs mt-1 hidden sm:block">Modern & Digital</div>
                </button>
                </div>
            </div>

            <Button 
              onClick={handleGenerate}
              disabled={!prompt.trim() || isGenerating}
              className="w-full bg-textile-accent hover:bg-textile-accent/90 text-sm sm:text-base"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin shrink-0" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="mr-2 h-4 w-4 shrink-0" />
                  Generate Branding Kit
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Preview Section */}
        <Card className="textile-hover textile-shadow">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="flex items-center text-lg sm:text-xl">
              <Eye className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-chart-2 shrink-0" />
              Generated Brand Kit
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            <div className="space-y-4 sm:space-y-6">
              {/* Error Display */}
              {error && (
                <div className="p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-xs sm:text-sm text-red-600 break-words">{error}</p>
                </div>
              )}

              {/* Preview Placeholder */}
              {!brandingData && (
                <div className="aspect-square bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-border">
                    <div className="text-center px-4">
                    <div className="w-12 h-12 sm:w-16 sm:h-16 bg-chart-1 rounded-lg mx-auto mb-3 sm:mb-4 flex items-center justify-center">
                      <Wand2 className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                    </div>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      {prompt ? "Your branding preview will appear here" : "Enter a prompt to generate your branding kit"}
                    </p>
                  </div>
                </div>
              )}

              {/* Generated Assets Preview */}
              {brandingData && (
                <div className="space-y-3 sm:space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-xs sm:text-sm font-medium">Logo Preview</Label>
                        {brandingData.logo && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => downloadImage(
                              brandingData.logo!.data,
                              `logo-${Date.now()}.${brandingData.logo!.format.toLowerCase()}`,
                              brandingData.logo!.format
                            )}
                            className="h-6 w-6 sm:h-7 sm:w-7 p-0"
                          >
                            <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                          </Button>
                        )}
                      </div>
                      <div className="aspect-square bg-background rounded border flex items-center justify-center p-3 sm:p-4">
                        {brandingData.logo ? (
                          /* eslint-disable-next-line @next/next/no-img-element */
                          <img 
                            src={`data:image/png;base64,${brandingData.logo.data}`}
                            alt="Generated Logo"
                            className="max-w-full max-h-full object-contain"
                          />
                        ) : (
                          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-chart-1 rounded flex items-center justify-center">
                            <span className="text-white font-bold text-sm sm:text-base">F</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-xs sm:text-sm font-medium">Color Palette</Label>
                        {brandingData.color_palette && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => downloadImage(
                              brandingData.color_palette!.data,
                              `color-palette-${Date.now()}.${brandingData.color_palette!.format.toLowerCase()}`,
                              brandingData.color_palette!.format
                            )}
                            className="h-6 w-6 sm:h-7 sm:w-7 p-0"
                          >
                            <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                          </Button>
                        )}
                      </div>
                      <div className="aspect-square bg-background rounded border flex items-center justify-center p-3 sm:p-4">
                        {brandingData.color_palette ? (
                          /* eslint-disable-next-line @next/next/no-img-element */
                          <img 
                            src={`data:image/png;base64,${brandingData.color_palette.data}`}
                            alt="Generated Color Palette"
                            className="max-w-full max-h-full object-contain"
                          />
                        ) : (
                          <div className="flex space-x-1">
                            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-chart-1 rounded"></div>
                            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-chart-2 rounded"></div>
                            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-chart-3 rounded"></div>
                            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-chart-4 rounded"></div>
                          </div>
                        )}
            </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="flex-1 text-xs sm:text-sm"
                      onClick={handleDownloadAll}
                    >
                      <Download className="mr-1 h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
                      Download All
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="flex-1 text-xs sm:text-sm"
                      onClick={handleGenerate}
                      disabled={isGenerating}
                    >
                      <RefreshCw className="mr-1 h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
                      Regenerate
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      </div>
  )
}
