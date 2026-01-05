"use client"

import { useState, useMemo, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Sparkles, AlertCircle } from "lucide-react"
import Image from "next/image"
import { buildApiUrl } from "@/utils/api"
import { useAuth } from "@/hooks/useAuth"

interface Template {
  id: string
  name: string
  description: string
  category: string
  subcategory: string
  audience: string[]
  offer: string
  thumbnail_url: string | null
  prompt: string
  is_active: boolean
  is_featured: boolean
}

interface TemplateResponse {
  id: string;
  name: string;
  description?: string;
  category?: string;
  subcategory?: string;
  audience?: string[];
  offer?: string;
  thumbnail_url?: string | null;
  prompt: string;
  is_active: boolean;
  is_featured: boolean;
}

export default function TemplatesPage() {
  const router = useRouter()
  const { getToken } = useAuth()
  const [templates, setTemplates] = useState<Template[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("All")
  const [selectedAudience, setSelectedAudience] = useState<string>("All")
  const [selectedOffer, setSelectedOffer] = useState<string>("All")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load templates from API
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Get auth token using useAuth hook (same as enhanced-poster-generator)
        const token = await getToken()
        const authHeaders: Record<string, string> = {
          'Content-Type': 'application/json',
        }
        if (token) {
          authHeaders['Authorization'] = `Bearer ${token}`
        }
        
        // Multitenancy: pass organization context if available (same as enhanced-poster-generator)
        try {
          const orgSlug = (typeof window !== 'undefined' ? window.localStorage.getItem('organizationSlug') : null)
            || process.env.NEXT_PUBLIC_ORGANIZATION_SLUG
          if (orgSlug) {
            authHeaders['X-Organization'] = orgSlug
          }
          const devOrgId = (typeof window !== 'undefined' ? window.localStorage.getItem('devOrgId') : null)
            || process.env.NEXT_PUBLIC_DEV_ORG_ID
          if (devOrgId) {
            authHeaders['X-Dev-Org-Id'] = devOrgId
          }
        } catch {}
        
        // Get Django backend URL - same logic as other API routes
        const getDjangoBackendUrl = () => {
          // Priority: NEXT_PUBLIC_API_URL > NEXT_PUBLIC_API_BASE_URL > development localhost
          if (process.env.NEXT_PUBLIC_API_URL) {
            return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '');
          }
          if (process.env.NEXT_PUBLIC_API_BASE_URL) {
            return process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/+$/, '');
          }
          // Development fallback
          if (process.env.NODE_ENV === 'development') {
            return 'http://localhost:8000';
          }
          // Production fallback
          return 'http://47.129.60.11';
        }
        
        // In development, use absolute URL to bypass Next.js rewrites
        // In production, use buildApiUrl for relative paths
        // Fetch all templates (both active and inactive) - frontend will filter by is_active if needed
        const apiUrl = process.env.NODE_ENV === 'development'
          ? `${getDjangoBackendUrl()}/api/ai/poster-templates/`
          : buildApiUrl('/api/ai/poster-templates/');
        
        console.log('[Templates Page] Fetching from:', apiUrl);
        
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: authHeaders,
          credentials: 'include',
        })
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => response.statusText)
          console.error(`[Templates Page] API error (${response.status}):`, errorText)
          throw new Error(`Failed to load templates: ${response.status} ${errorText}`)
        }
        
        // Safely parse JSON, checking for HTML
        const text = await response.text()
        if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html') || text.trim().startsWith('<!')) {
          throw new Error('Backend returned HTML error page instead of JSON')
        }
        const data = JSON.parse(text)
        
        // Enhanced logging to debug response structure
        console.log('[Templates Page] Response status:', response.status)
        console.log('[Templates Page] Response data type:', typeof data)
        console.log('[Templates Page] Response is array:', Array.isArray(data))
        console.log('[Templates Page] Response keys:', data && typeof data === 'object' ? Object.keys(data) : 'N/A')
        console.log('[Templates Page] Full response data:', data)
        
        // Handle both list and paginated responses (same as enhanced-poster-generator)
        const templatesList = Array.isArray(data) ? data : (data.results || [])
        console.log(`[Templates Page] Loaded ${templatesList.length} templates from API`)
        
        // Transform API response to match expected format
        // Show all templates (both active and inactive) - user can filter if needed
        const transformedTemplates = templatesList.map((t: TemplateResponse) => ({
          id: t.id,
          name: t.name,
          description: t.description || '',
          category: t.category || '',
          subcategory: t.subcategory || '',
          audience: Array.isArray(t.audience) ? t.audience : [],
          offer: t.offer || 'No Offer',
          thumbnail_url: t.thumbnail_url || null,
          prompt: t.prompt,
          is_active: t.is_active,
          is_featured: t.is_featured,
        }))
        
        console.log(`[Templates Page] Transformed ${transformedTemplates.length} templates`)
        setTemplates(transformedTemplates)
      } catch (err) {
        console.error("Error loading templates:", err)
        setError(err instanceof Error ? err.message : 'Failed to load templates')
        setTemplates([])
      } finally {
        setLoading(false)
      }
    }
    loadTemplates()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(templates.map(t => t.category).filter(Boolean))
    return ["All", ...Array.from(cats).sort()]
  }, [templates])

  // Filter templates based on search, category, audience, and offer
  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
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
    // Set flag to indicate we're navigating from templates page
    // This helps preserve uploaded images when selecting a template
    sessionStorage.setItem('posterGenerator_fromTemplates', 'true')
    
    // Navigate to poster-generator with prompt as query parameter
    try {
      // Use encodeURIComponent to properly encode the prompt
      const encodedPrompt = encodeURIComponent(template.prompt)
      router.push(`/dashboard/poster-generator?prompt=${encodedPrompt}`)
    } catch (error) {
      console.error('Error encoding prompt:', error)
      // Fallback: try to navigate with a basic encoding
      const safePrompt = template.prompt.replace(/\s+/g, '+')
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

  if (error) {
    return (
      <div className="space-y-8 lg:space-y-12">
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Error Loading Templates</h2>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 lg:space-y-12">
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
        <CardContent className="p-6 space-y-4 pb-8">
          {/* Filter Dropdowns */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
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

            {/* Search */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search templates..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <Sparkles className="h-12 w-12 mx-auto mb-4 animate-pulse text-muted-foreground" />
            <p className="text-muted-foreground">Loading templates...</p>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-destructive" />
            <p className="text-destructive font-medium mb-2">Error loading templates</p>
            <p className="text-sm text-muted-foreground">{error}</p>
            <p className="text-xs text-muted-foreground mt-4">
              Please check that the backend server is running and try refreshing the page.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Results Count */}
      {!loading && !error && (
        <div className="text-sm text-muted-foreground">
          Showing {filteredTemplates.length} of {templates.length} templates
        </div>
      )}

      {/* Templates Grid */}
      {!loading && !error && (
        <>
          {filteredTemplates.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                {templates.length === 0 ? (
                  <>
                    <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground font-medium mb-2">No templates available</p>
                    <p className="text-sm text-muted-foreground">
                      There are no templates in the database. Please contact an administrator to add templates.
                    </p>
                  </>
                ) : (
                  <p className="text-muted-foreground">No templates found matching your search criteria.</p>
                )}
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
                      {template.thumbnail_url ? (
                        <Image
                          src={template.thumbnail_url}
                          alt={template.name}
                          fill
                          className="object-cover"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                          unoptimized
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-100">
                          <Sparkles className="h-12 w-12 text-gray-400" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors flex items-center justify-center">
                        <Sparkles className="h-8 w-8 text-white opacity-0 hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-foreground line-clamp-1">{template.name}</h3>
                        {template.category && (
                          <Badge variant="outline" className="text-xs">
                            {template.category}
                          </Badge>
                        )}
                      </div>
                      {template.description && (
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {template.description}
                        </p>
                      )}
                      {template.audience && template.audience.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {template.audience.map((aud, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {aud}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <div className="flex items-center justify-between">
                        {template.subcategory && (
                          <p className="text-xs text-muted-foreground">
                            {template.subcategory}
                          </p>
                        )}
                        {template.offer && template.offer !== "No Offer" && (
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
        </>
      )}
    </div>
  )
}
