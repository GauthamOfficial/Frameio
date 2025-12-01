import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ShareButtons } from "@/components/poster/ShareButtons"

interface PosterData {
  id: string
  image_url: string
  public_url?: string  // Cloudinary URL for sharing
  caption: string
  full_caption: string
  hashtags: string[]
  prompt: string
  aspect_ratio: string
  width: number
  height: number
  generated_at: string
  branding_applied: boolean
  logo_added: boolean
  contact_info_added: boolean
}

interface PosterPageProps {
  params: Promise<{
    id: string
  }>
}

// Function to fetch poster data from API
async function getPosterData(id: string): Promise<PosterData | null> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/ai/ai-poster/poster/${id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      console.error('Failed to fetch poster:', response.status, response.statusText)
      // Return mock data for testing
      return {
        id,
        image_url: `http://localhost:8000/media/generated_posters/poster_${id}.png`,
        caption: "Check out this amazing AI-generated poster!",
        full_caption: "Check out this amazing AI-generated poster! Created with cutting-edge AI technology. #AI #Poster #Design #Innovation",
        hashtags: ["#AI", "#Poster", "#Design", "#Innovation"],
        prompt: "Create a modern textile poster for a silk saree brand",
        aspect_ratio: "4:5",
        width: 1080,
        height: 1350,
        generated_at: new Date().toISOString(),
        branding_applied: false,
        logo_added: false,
        contact_info_added: false
      }
    }
    
    const data = await response.json()
    return data.success ? data.poster : null
  } catch (error) {
    console.error('Error fetching poster data:', error)
    // Return mock data for testing
    return {
      id,
      image_url: `http://localhost:8000/media/generated_posters/poster_${id}.png`,
      caption: "Check out this amazing AI-generated poster!",
      full_caption: "Check out this amazing AI-generated poster! Created with cutting-edge AI technology. #AI #Poster #Design #Innovation",
      hashtags: ["#AI", "#Poster", "#Design", "#Innovation"],
      prompt: "Create a modern textile poster for a silk saree brand",
      aspect_ratio: "4:5",
      width: 1080,
      height: 1350,
      generated_at: new Date().toISOString(),
      branding_applied: false,
      logo_added: false,
      contact_info_added: false
    }
  }
}

export async function generateMetadata({ params }: PosterPageProps): Promise<Metadata> {
  const { id } = await params
  const poster = await getPosterData(id)
  
  if (!poster) {
    return {
      title: 'Poster Not Found',
      description: 'The requested poster could not be found.'
    }
  }

  // Try to get ngrok URL for public sharing
  let pageUrl = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/poster/${id}`
  
  try {
    // Check if we're in a browser environment and ngrok is available
    if (typeof window === 'undefined') {
      // Server-side: try to detect ngrok URL
      const response = await fetch('http://localhost:4040/api/tunnels', {
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(1000)
      })
      
      if (response.ok) {
        const data = await response.json()
        const tunnels = data.tunnels || []
        const httpsTunnel = tunnels.find((t: { proto: string; config: { addr: string }; public_url: string }) => 
          t.proto === 'https' && 
          t.config.addr.includes('3000')
        )
        
        if (httpsTunnel) {
          pageUrl = `${httpsTunnel.public_url}/poster/${id}`
        }
      }
    }
  } catch {
    // Silently fall back to localhost URL
    console.log('Ngrok not available, using localhost URL')
  }
  
  return {
    title: poster.caption,
    description: poster.full_caption,
    openGraph: {
      type: 'article',
      title: poster.caption,
      description: poster.full_caption,
      url: pageUrl,
      images: [
        {
          url: poster.public_url || poster.image_url,  // Use Cloudinary URL for better sharing
          width: poster.width,
          height: poster.height,
          alt: poster.caption,
        },
      ],
      siteName: 'Framio AI Poster Generator',
    },
    twitter: {
      card: 'summary_large_image',
      title: poster.caption,
      description: poster.full_caption,
      images: [poster.public_url || poster.image_url],  // Use Cloudinary URL
    },
    other: {
      'og:image:width': poster.width.toString(),
      'og:image:height': poster.height.toString(),
    },
  }
}

export default async function PosterPage({ params }: PosterPageProps) {
  const { id } = await params
  const poster = await getPosterData(id)
  
  if (!poster) {
    notFound()
  }

  // Try to get ngrok URL for public sharing
  let pageUrl = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/poster/${id}`
  
  try {
    // Check if we're in a browser environment and ngrok is available
    if (typeof window === 'undefined') {
      // Server-side: try to detect ngrok URL
      const response = await fetch('http://localhost:4040/api/tunnels', {
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(1000)
      })
      
      if (response.ok) {
        const data = await response.json()
        const tunnels = data.tunnels || []
        const httpsTunnel = tunnels.find((t: { proto: string; config: { addr: string }; public_url: string }) => 
          t.proto === 'https' && 
          t.config.addr.includes('3000')
        )
        
        if (httpsTunnel) {
          pageUrl = `${httpsTunnel.public_url}/poster/${id}`
        }
      }
    }
  } catch {
    // Silently fall back to localhost URL
    console.log('Ngrok not available, using localhost URL')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-gray-800 mb-2">
              AI-Generated Poster
            </CardTitle>
            <p className="text-gray-600">
              Created with Framio AI Poster Generator
            </p>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Poster Image */}
            <div className="relative bg-white rounded-lg overflow-hidden shadow-lg">
              <div className="aspect-[4/5] relative">
                <Image
                  src={poster.image_url}
                  alt={poster.caption}
                  fill
                  className="object-contain"
                  priority
                />
              </div>
            </div>

            {/* Poster Details */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Left Column - Poster Info */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Caption</h3>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {poster.full_caption}
                  </p>
                </div>

                {poster.hashtags.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Hashtags</h3>
                    <div className="flex flex-wrap gap-2">
                      {poster.hashtags.map((hashtag, index) => (
                        <Badge key={index} variant="secondary" className="text-sm">
                          {hashtag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Generation Details</h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Aspect Ratio:</strong> {poster.aspect_ratio}</p>
                    <p><strong>Dimensions:</strong> {poster.width} × {poster.height}</p>
                    <p><strong>Generated:</strong> {new Date(poster.generated_at).toLocaleDateString()}</p>
                    {poster.branding_applied && (
                      <p className="text-green-600"><strong>✓ Branding Applied</strong></p>
                    )}
                    {poster.logo_added && (
                      <p className="text-green-600"><strong>✓ Logo Added</strong></p>
                    )}
                    {poster.contact_info_added && (
                      <p className="text-green-600"><strong>✓ Contact Info Added</strong></p>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column - Sharing Options */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">Share This Poster</h3>
                
                <div className="space-y-3">
                  <ShareButtons 
                    poster={poster} 
                    pageUrl={pageUrl}
                  />
                </div>

              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

