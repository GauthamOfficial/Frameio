"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Plus, Palette, Download, Eye, Calendar, Share2 } from "lucide-react"
import React, { useState } from "react"
import { useToastHelpers } from "@/components/common"
import { useAppContext } from "@/contexts/app-context"
import { apiClient } from "@/lib/api-client"

export default function CatalogBuilder() {
  const { showSuccess, showError } = useToastHelpers()
  const appContext = useAppContext()
  const { token } = appContext || { token: null }
  const [selectedProducts, setSelectedProducts] = useState<number[]>([])
  
  // Set token in API client
  React.useEffect(() => {
    if (token) {
      apiClient.setToken(token)
    }
  }, [token])
  const [isCreating, setIsCreating] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [isScheduling, setIsScheduling] = useState(false)
  const [isPosting, setIsPosting] = useState(false)
  const [generatedCatalog, setGeneratedCatalog] = useState<{
    url: string
    name: string
  } | null>(null)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [scheduleData, setScheduleData] = useState({
    platform: 'instagram',
    scheduledTime: '',
    caption: ''
  })

  const products = [
    { id: 1, name: "Silk Saree Collection", color: "Deep Navy", pattern: "Floral", price: "$299" },
    { id: 2, name: "Cotton Kurta Set", color: "Maroon", pattern: "Geometric", price: "$149" },
    { id: 3, name: "Linen Dress", color: "Beige", pattern: "Striped", price: "$199" },
    { id: 4, name: "Chiffon Scarf", color: "Pastel Blue", pattern: "Abstract", price: "$79" },
  ]

  const handleAddProduct = (productId: number) => {
    setSelectedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    )
  }

  const handleCreateCatalog = async () => {
    if (selectedProducts.length === 0) {
      showError("Please select at least one product for the catalog")
      return
    }

    setIsCreating(true)
    try {
      // Create catalog using AI service
      const result = await apiClient.createCatalog({
        product_ids: selectedProducts,
        template: 'festival_collection',
        style: 'modern',
        color_scheme: 'deep_navy_gold'
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to create catalog')
      }
      
      const data = result.data!
      setGeneratedCatalog({
        url: data.catalog_url,
        name: data.catalog_name
      })
      
      showSuccess("Catalog created successfully!")
    } catch (error) {
      showError(`Failed to create catalog: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsCreating(false)
    }
  }

  const handleDownload = async () => {
    if (!generatedCatalog) {
      showError("No catalog to download")
      return
    }
    
    setIsDownloading(true)
    try {
      const success = await apiClient.downloadFile(
        generatedCatalog.url, 
        `${generatedCatalog.name}-${Date.now()}.pdf`
      )
      
      if (success) {
        showSuccess("Catalog downloaded successfully!")
      } else {
        throw new Error('Download failed')
      }
    } catch (error) {
      showError(`Failed to download catalog: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleSchedule = () => {
    if (!generatedCatalog) {
      showError("Please create a catalog first")
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
        asset_url: generatedCatalog.url,
        caption: scheduleData.caption,
        scheduled_time: scheduleData.scheduledTime,
        metadata: {
          type: 'catalog',
          generated_at: new Date().toISOString()
        }
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to schedule post')
      }
      
      showSuccess("Catalog post scheduled successfully!")
      setShowScheduleModal(false)
      setScheduleData({ platform: 'instagram', scheduledTime: '', caption: '' })
    } catch (error) {
      showError(`Failed to schedule post: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsScheduling(false)
    }
  }

  const handlePostNow = async () => {
    if (!generatedCatalog) {
      showError("Please create a catalog first")
      return
    }
    
    setIsPosting(true)
    try {
      const result = await apiClient.postToSocialMedia({
        platform: 'instagram',
        asset_url: generatedCatalog.url,
        caption: `Check out our latest ${generatedCatalog.name}! 🎨✨ #textile #catalog #fashion`,
        metadata: {
          type: 'catalog'
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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Catalog Builder</h1>
          <p className="text-muted-foreground mt-1">
            Create beautiful product catalogs with AI-powered color matching.
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            className="bg-textile-accent"
            onClick={handleCreateCatalog}
            disabled={isCreating || selectedProducts.length === 0}
          >
            <Plus className="mr-2 h-4 w-4" />
            {isCreating ? "Creating..." : `Create Catalog (${selectedProducts.length})`}
          </Button>
          
          {generatedCatalog && (
            <>
              <Button 
                variant="outline"
                onClick={handleDownload}
                disabled={isDownloading}
              >
                <Download className="mr-2 h-4 w-4" />
                {isDownloading ? "Downloading..." : "Download"}
              </Button>
              <Button 
                variant="outline"
                onClick={handleSchedule}
                disabled={isScheduling}
              >
                <Calendar className="mr-2 h-4 w-4" />
                {isScheduling ? "Scheduling..." : "Schedule"}
              </Button>
              <Button 
                variant="outline"
                onClick={handlePostNow}
                disabled={isPosting}
              >
                <Share2 className="mr-2 h-4 w-4" />
                {isPosting ? "Posting..." : "Post Now"}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* AI Suggestions */}
      <Card className="textile-hover textile-shadow">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Palette className="mr-2 h-5 w-5 text-chart-2" />
            AI Color Suggestions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary" className="bg-chart-1 text-white">Deep Navy + Gold</Badge>
            <Badge variant="secondary" className="bg-chart-2 text-white">Maroon + Cream</Badge>
            <Badge variant="secondary" className="bg-chart-3 text-white">Beige + Sage</Badge>
            <Badge variant="secondary" className="bg-chart-4 text-white">Pastel + Navy</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => {
          const isSelected = selectedProducts.includes(product.id)
          return (
            <Card 
              key={product.id} 
              className={`textile-hover textile-shadow transition-all ${
                isSelected ? 'ring-2 ring-primary' : ''
              }`}
            >
              <CardContent className="p-0">
                <div className="aspect-square bg-muted rounded-t-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-chart-1 rounded-lg mx-auto mb-2"></div>
                    <p className="text-xs text-muted-foreground">Product Image</p>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-foreground mb-2">{product.name}</h3>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <p>Color: {product.color}</p>
                    <p>Pattern: {product.pattern}</p>
                    <p className="font-medium text-foreground">{product.price}</p>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Eye className="mr-1 h-3 w-3" />
                      View
                    </Button>
                    <Button 
                      size="sm" 
                      variant={isSelected ? "default" : "outline"}
                      className="flex-1"
                      onClick={() => handleAddProduct(product.id)}
                    >
                      <Download className="mr-1 h-3 w-3" />
                      {isSelected ? "Added" : "Add"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Template Selection */}
      <Card className="textile-hover textile-shadow">
        <CardHeader>
          <CardTitle>Catalog Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-1 rounded-lg mx-auto mb-2"></div>
                <p className="text-sm text-muted-foreground">Festival Collection</p>
              </div>
            </div>
            <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-2 rounded-lg mx-auto mb-2"></div>
                <p className="text-sm text-muted-foreground">Wedding Collection</p>
              </div>
            </div>
            <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-3 rounded-lg mx-auto mb-2"></div>
                <p className="text-sm text-muted-foreground">Casual Wear</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Generated Catalog Preview */}
      {generatedCatalog && (
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Generated Catalog</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center mb-4 overflow-hidden">
              <img
                src={generatedCatalog.url}
                alt={generatedCatalog.name}
                className="w-full h-full object-cover rounded-lg"
              />
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                onClick={handleDownload}
                disabled={isDownloading}
                className="flex-1"
              >
                <Download className="mr-2 h-4 w-4" />
                {isDownloading ? "Downloading..." : "Download"}
              </Button>
              <Button 
                variant="outline"
                onClick={handleSchedule}
                disabled={isScheduling}
                className="flex-1"
              >
                <Calendar className="mr-2 h-4 w-4" />
                {isScheduling ? "Scheduling..." : "Schedule"}
              </Button>
              <Button 
                variant="outline"
                onClick={handlePostNow}
                disabled={isPosting}
                className="flex-1"
              >
                <Share2 className="mr-2 h-4 w-4" />
                {isPosting ? "Posting..." : "Post Now"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Schedule Catalog Post</CardTitle>
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
                <input
                  id="scheduledTime"
                  type="datetime-local"
                  value={scheduleData.scheduledTime}
                  onChange={(e) => setScheduleData(prev => ({ ...prev, scheduledTime: e.target.value }))}
                  min={new Date().toISOString().slice(0, 16)}
                  className="w-full p-2 border rounded-md"
                />
              </div>
              
              <div>
                <Label htmlFor="caption">Caption</Label>
                <textarea
                  id="caption"
                  value={scheduleData.caption}
                  onChange={(e) => setScheduleData(prev => ({ ...prev, caption: e.target.value }))}
                  placeholder="Enter your post caption..."
                  rows={3}
                  className="w-full p-2 border rounded-md"
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
