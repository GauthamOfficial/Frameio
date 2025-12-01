"use client"

import { useState, useMemo, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Sparkles } from "lucide-react"
import Image from "next/image"

interface Template {
  id: string
  title: string
  category: string
  subcategory: string
  audience: string[]
  offer: string
  image: string
  caption: string
}

export default function TemplatesPage() {
  const router = useRouter()
  const [templates, setTemplates] = useState<Template[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("All")
  const [selectedAudience, setSelectedAudience] = useState<string>("All")
  const [selectedOffer, setSelectedOffer] = useState<string>("All")
  const [loading, setLoading] = useState(true)

  // Load templates from JSON file
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await fetch("/Templates/prompts.txt")
        const data = await response.json()
        setTemplates(data)
      } catch (error) {
        console.error("Error loading templates:", error)
      } finally {
        setLoading(false)
      }
    }
    loadTemplates()
  }, [])

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(templates.map(t => t.category))
    return ["All", ...Array.from(cats).sort()]
  }, [templates])

  // Filter templates based on search, category, audience, and offer
  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = 
        template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.subcategory.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.audience.some(aud => aud.toLowerCase().includes(searchQuery.toLowerCase()))
      
      const matchesCategory = selectedCategory === "All" || template.category === selectedCategory
      
      const matchesAudience = 
        selectedAudience === "All" || 
        template.audience.includes(selectedAudience)
      
      const matchesOffer = 
        selectedOffer === "All" ||
        (selectedOffer === "With Offer" && template.offer !== "No Offer") ||
        (selectedOffer === "Without Offer" && template.offer === "No Offer")
      
      return matchesSearch && matchesCategory && matchesAudience && matchesOffer
    })
  }, [templates, searchQuery, selectedCategory, selectedAudience, selectedOffer])

  const handleTemplateClick = (template: Template) => {
    // Navigate to poster-generator with prompt as query parameter
    try {
      // Use encodeURIComponent to properly encode the prompt
      const encodedPrompt = encodeURIComponent(template.caption)
      router.push(`/dashboard/poster-generator?prompt=${encodedPrompt}`)
    } catch (error) {
      console.error('Error encoding prompt:', error)
      // Fallback: try to navigate with a basic encoding
      const safePrompt = template.caption.replace(/\s+/g, '+')
      router.push(`/dashboard/poster-generator?prompt=${safePrompt}`)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading templates...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Templates Library</h1>
          <p className="text-muted-foreground mt-1">
            Choose from pre-designed textile festival and event templates. Click on any template to use its prompt.
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="textile-hover textile-shadow">
        <CardContent className="p-6 space-y-4">
          {/* Filter Dropdowns */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Category Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Category</label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder={selectedCategory || "Select category"} />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {/* Search Bar - Under Category */}
              <div className="relative mt-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search templates..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Audience Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Audience</label>
              <Select value={selectedAudience} onValueChange={setSelectedAudience}>
                <SelectTrigger>
                  <SelectValue placeholder={selectedAudience || "Select audience"} />
                </SelectTrigger>
                <SelectContent>
                  {["All", "Men", "Women", "Kids"].map((audience) => (
                    <SelectItem key={audience} value={audience}>
                      {audience}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Offer Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Offer</label>
              <Select value={selectedOffer} onValueChange={setSelectedOffer}>
                <SelectTrigger>
                  <SelectValue placeholder={selectedOffer || "Select offer"} />
                </SelectTrigger>
                <SelectContent>
                  {["All", "With Offer", "Without Offer"].map((offer) => (
                    <SelectItem key={offer} value={offer}>
                      {offer}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        Showing {filteredTemplates.length} of {templates.length} templates
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No templates found matching your search criteria.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map((template) => (
            <Card 
              key={template.id} 
              className="textile-hover textile-shadow cursor-pointer transition-all hover:shadow-lg"
              onClick={() => handleTemplateClick(template)}
            >
              <CardContent className="p-0">
                <div className="aspect-[4/3] relative bg-muted rounded-t-lg overflow-hidden">
                  <Image
                    src={`/Templates/${template.image}`}
                    alt={template.title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    unoptimized
                  />
                  <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors flex items-center justify-center">
                    <Sparkles className="h-8 w-8 text-white opacity-0 hover:opacity-100 transition-opacity" />
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-foreground line-clamp-1">{template.title}</h3>
                    <Badge variant="outline" className="text-xs">
                      {template.category}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {template.audience.map((aud, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {aud}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-muted-foreground">
                      {template.subcategory}
                    </p>
                    {template.offer !== "No Offer" && (
                      <Badge className="text-xs bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-300 dark:border-orange-700 hover:bg-orange-500/20">
                        {template.offer}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
