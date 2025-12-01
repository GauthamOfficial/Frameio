"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  Sparkles, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  Wand2,
  Image as ImageIcon
} from "lucide-react"

interface TestResult {
  success: boolean
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any
  error?: string
  processingTime?: number
  refinedPrompt?: string
  twoStepFlow?: boolean
}

export default function TestTwoStepIntegration() {
  const [isLoading, setIsLoading] = useState(false)
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [generationStep, setGenerationStep] = useState<'idle' | 'refining' | 'generating' | 'completed'>('idle')
  const [imageLoading, setImageLoading] = useState<boolean>(false)
  const [usingFallback, setUsingFallback] = useState<boolean>(false)
  
  // Debug function to track fallback state changes
  const setUsingFallbackWithDebug = (value: boolean, reason: string) => {
    console.log(`🔄 Fallback state changed to ${value}: ${reason}`)
    setUsingFallback(value)
  }
  
  // Test parameters
  const [testParams, setTestParams] = useState({
    customText: "Create a stunning silk saree poster for Deepavali festival",
    fabricType: "silk",
    festival: "deepavali",
    style: "traditional",
    priceRange: "₹5000-₹15000",
    offerDetails: "50% Off Festival Special",
    colorScheme: "gold, red, maroon"
  })

  const handleTestIntegration = async () => {
    setIsLoading(true)
    setTestResult(null)
    setGenerationStep('idle')
    setImageLoading(false)
    setUsingFallbackWithDebug(false, 'Starting new test')
    
    try {
      console.log('🚀 Starting two-step integration test...')
      
      // Using test endpoint - no authentication required
      console.log('🧪 Using test endpoint (no authentication required)')
      
      // Step 1: Show prompt refinement
      setGenerationStep('refining')
      console.log('Step 1: Refining prompt with Gemini 2.5 Flash...')
      
      // Step 2: Show image generation
      setGenerationStep('generating')
      console.log('Step 2: Generating image with NanoBanana...')
      
      const startTime = Date.now()
      
      // Use real backend API with Gemini + NanoBanana integration
      console.log('🚀 Using real backend API with Gemini + NanoBanana...')
      
      // Use test endpoint that doesn't require authentication
      const response = await fetch('http://localhost:8000/api/test/two-step/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          custom_text: testParams.customText,
          fabric_type: testParams.fabricType,
          festival: testParams.festival,
          price_range: testParams.priceRange,
          style: testParams.style,
          offer_details: testParams.offerDetails,
          color_scheme: testParams.colorScheme,
          generation_type: 'poster'
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const result = await response.json()
      
      const endTime = Date.now()
      const processingTime = (endTime - startTime) / 1000
      
      // Step 3: Show completion
      setGenerationStep('completed')
      
      if (result.success) {
        console.log('🖼️ Generated Image URL:', result.poster_url)
        console.log('📊 Full result data:', result)
        console.log('✅ Real AI generation completed successfully!')
        
        setTestResult({
          success: true,
          data: result,
          processingTime,
          refinedPrompt: result.metadata?.refined_prompt,
          twoStepFlow: result.metadata?.two_step_flow
        })
        console.log('✅ Two-step integration test successful!', result)
      } else {
        setTestResult({
          success: false,
          error: result.error || 'Unknown error',
          processingTime
        })
        console.error('❌ Two-step integration test failed:', result.error)
      }
      
    } catch (error) {
      setTestResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        processingTime: 0
      })
      console.error('❌ Two-step integration test failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Two-Step AI Integration Test
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Test Parameters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="customText">Custom Text</Label>
              <Textarea
                id="customText"
                value={testParams.customText}
                onChange={(e) => setTestParams(prev => ({ ...prev, customText: e.target.value }))}
                placeholder="Enter your prompt..."
                rows={3}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="fabricType">Fabric Type</Label>
              <Input
                id="fabricType"
                value={testParams.fabricType}
                onChange={(e) => setTestParams(prev => ({ ...prev, fabricType: e.target.value }))}
                placeholder="silk, cotton, etc."
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="festival">Festival</Label>
              <Input
                id="festival"
                value={testParams.festival}
                onChange={(e) => setTestParams(prev => ({ ...prev, festival: e.target.value }))}
                placeholder="deepavali, pongal, etc."
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="style">Style</Label>
              <Input
                id="style"
                value={testParams.style}
                onChange={(e) => setTestParams(prev => ({ ...prev, style: e.target.value }))}
                placeholder="traditional, modern, etc."
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="priceRange">Price Range</Label>
              <Input
                id="priceRange"
                value={testParams.priceRange}
                onChange={(e) => setTestParams(prev => ({ ...prev, priceRange: e.target.value }))}
                placeholder="₹5000-₹15000"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="colorScheme">Color Scheme</Label>
              <Input
                id="colorScheme"
                value={testParams.colorScheme}
                onChange={(e) => setTestParams(prev => ({ ...prev, colorScheme: e.target.value }))}
                placeholder="gold, red, maroon"
              />
            </div>
          </div>
          
          {/* Test Button */}
          <Button 
            onClick={handleTestIntegration} 
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Testing Integration...
              </>
            ) : (
              <>
                <Wand2 className="h-4 w-4 mr-2" />
                Test Two-Step Integration
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generation Steps */}
      {generationStep !== 'idle' && (
        <Card>
          <CardHeader>
            <CardTitle>Generation Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Step 1: Prompt Refinement */}
              <div className={`flex items-center gap-3 p-3 rounded-lg ${
                generationStep === 'refining' ? 'bg-blue-50 border-blue-200' : 
                generationStep === 'generating' || generationStep === 'completed' ? 'bg-green-50 border-green-200' : 
                'bg-gray-50 border-gray-200'
              } border`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  generationStep === 'refining' ? 'bg-blue-500 text-white' : 
                  generationStep === 'generating' || generationStep === 'completed' ? 'bg-green-500 text-white' : 
                  'bg-gray-300 text-gray-600'
                }`}>
                  {generationStep === 'refining' ? <Loader2 className="h-4 w-4 animate-spin" /> : 
                   generationStep === 'generating' || generationStep === 'completed' ? <CheckCircle className="h-4 w-4" /> : 
                   '1'}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Step 1: Prompt Refinement</h4>
                  <p className="text-sm text-muted-foreground">
                    Using Gemini 2.5 Flash to enhance your prompt
                  </p>
                </div>
              </div>

              {/* Step 2: Image Generation */}
              <div className={`flex items-center gap-3 p-3 rounded-lg ${
                generationStep === 'generating' ? 'bg-blue-50 border-blue-200' : 
                generationStep === 'completed' ? 'bg-green-50 border-green-200' : 
                'bg-gray-50 border-gray-200'
              } border`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  generationStep === 'generating' ? 'bg-blue-500 text-white' : 
                  generationStep === 'completed' ? 'bg-green-500 text-white' : 
                  'bg-gray-300 text-gray-600'
                }`}>
                  {generationStep === 'generating' ? <Loader2 className="h-4 w-4 animate-spin" /> : 
                   generationStep === 'completed' ? <CheckCircle className="h-4 w-4" /> : 
                   '2'}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Step 2: Image Generation</h4>
                  <p className="text-sm text-muted-foreground">
                    Using NanoBanana to generate high-quality image
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Test Results */}
      {testResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {testResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
              Test Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Status */}
            <div className="flex items-center gap-2">
              <Badge variant={testResult.success ? "default" : "destructive"}>
                {testResult.success ? "SUCCESS" : "FAILED"}
              </Badge>
              {testResult.processingTime && (
                <Badge variant="outline">
                  {testResult.processingTime.toFixed(2)}s
                </Badge>
              )}
              {testResult.twoStepFlow && (
                <Badge variant="secondary">
                  Two-Step Flow
                </Badge>
              )}
            </div>

            {/* Refined Prompt */}
            {testResult.refinedPrompt && (
              <div className="space-y-2">
                <h4 className="font-medium">Refined Prompt:</h4>
                <p className="text-sm text-muted-foreground italic bg-muted p-3 rounded">
                  {testResult.refinedPrompt}
                </p>
              </div>
            )}

            {/* Generated Image */}
            {testResult.success && testResult.data?.poster_url && (
              <div className="space-y-2">
                <h4 className="font-medium">Generated Image:</h4>
                <div className="flex items-center gap-2">
                  <ImageIcon className="h-4 w-4" />
                  <a 
                    href={testResult.data.poster_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    View Generated Image
                  </a>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Image Source: {testResult.data.poster_url.startsWith('data:') ? 'Local SVG' : 'AI Generated Image'}
                  </p>
                  {!testResult.data.poster_url.startsWith('data:') && (
                    <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded">
                      <CheckCircle className="h-4 w-4" />
                      Real AI Generated Image (Gemini + NanoBanana)
                    </div>
                  )}
                  {usingFallback && (
                    <div className="flex items-center gap-2 text-sm text-orange-600 bg-orange-50 p-2 rounded">
                      <AlertCircle className="h-4 w-4" />
                      Using fallback image (original failed to load)
                      <div className="text-xs text-orange-500 mt-1">
                        Debug: This should not happen with local SVG images
                      </div>
                    </div>
                  )}
                  {imageLoading && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Loading image...
                    </div>
                  )}
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    key={`poster-${testResult.data.poster_url.substring(0, 50)}`}
                    src={testResult.data.poster_url} 
                    alt="Generated poster" 
                    className="max-w-md rounded-lg border"
                    onLoadStart={() => {
                      console.log('🔄 Image loading started:', testResult.data.poster_url.substring(0, 50) + '...')
                      setImageLoading(true)
                    }}
                    onLoad={() => {
                      console.log('✅ Image loaded successfully')
                      setImageLoading(false)
                      setUsingFallbackWithDebug(false, 'Image loaded successfully') // Reset fallback state on successful load
                    }}
                    onError={(e) => {
                      console.error('❌ Image failed to load:', e)
                      console.log('🖼️ Failed image URL:', e.currentTarget.src)
                      console.log('🔄 Is local SVG?', e.currentTarget.src.startsWith('data:'))
                      setImageLoading(false)
                      
                      // Only use fallback if it's not already a local SVG
                      if (!e.currentTarget.src.startsWith('data:') && testResult.data?.fallback_url) {
                        console.log('🔄 Attempting fallback to:', testResult.data.fallback_url)
                        e.currentTarget.src = testResult.data.fallback_url
                        setUsingFallbackWithDebug(true, 'External image failed, using fallback')
                        console.log('✅ Fallback image set')
                      } else if (e.currentTarget.src.startsWith('data:')) {
                        console.log('⚠️ Local SVG failed to load - this might be an encoding issue')
                        // Don't set fallback for local SVG failures - this might be a React re-render issue
                        console.log('🔄 Retrying with same local SVG...')
                        // Force a re-render by updating the src slightly
                        const currentSrc = e.currentTarget.src
                        e.currentTarget.src = ''
                        setTimeout(() => {
                          e.currentTarget.src = currentSrc
                        }, 100)
                      } else {
                        console.error('❌ No fallback URL available')
                      }
                    }}
                  />
                  
                  {/* Test fallback button */}
                  {testResult.data?.test_fallback_url && (
                    <div className="mt-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          console.log('🧪 Testing fallback image manually')
                          const img = document.querySelector('img[alt="Generated poster"]') as HTMLImageElement
                          if (img && testResult.data?.test_fallback_url) {
                            img.src = testResult.data.test_fallback_url
                            setUsingFallbackWithDebug(true, 'Manual fallback test triggered')
                            console.log('✅ Manual fallback triggered')
                          }
                        }}
                      >
                        Test Fallback Image
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Captions */}
            {testResult.success && testResult.data?.caption_suggestions && (
              <div className="space-y-2">
                <h4 className="font-medium">Caption Suggestions:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {testResult.data.caption_suggestions.map((caption: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-muted-foreground">•</span>
                      <span>{caption}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Error */}
            {!testResult.success && testResult.error && (
              <div className="space-y-2">
                <h4 className="font-medium text-red-600">Error:</h4>
                <p className="text-sm text-red-600 bg-red-50 p-3 rounded">
                  {testResult.error}
                </p>
              </div>
            )}

            {/* Metadata */}
            {testResult.success && testResult.data?.metadata && (
              <div className="space-y-2">
                <h4 className="font-medium">Metadata:</h4>
                <pre className="text-xs bg-muted p-3 rounded overflow-auto">
                  {JSON.stringify(testResult.data.metadata, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
