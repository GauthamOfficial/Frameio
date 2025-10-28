/**
 * Tunnel URL Detection Utility
 * Automatically detects ngrok or Cloudflare Tunnel URLs for Facebook sharing
 */

export interface NgrokTunnel {
  name: string
  uri: string
  public_url: string
  proto: string
  config: {
    addr: string
    inspect: boolean
  }
  metrics: {
    conns: {
      count: number
      gauge: number
      rate1: number
      rate15: number
      rate5: number
    }
    http: {
      count: number
      rate1: number
      rate15: number
      rate5: number
      resp_average: number
      resp_50: number
      resp_90: number
      resp_95: number
      resp_99: number
    }
  }
}

export interface NgrokResponse {
  tunnels: NgrokTunnel[]
  uri: string
}

/**
 * Get the current ngrok URL for the frontend (port 3000)
 */
export async function getNgrokUrl(): Promise<string | null> {
  try {
    const response = await fetch('http://localhost:4040/api/tunnels')
    
    if (!response.ok) {
      console.warn('Ngrok API not accessible:', response.status)
      return null
    }
    
    const data: NgrokResponse = await response.json()
    const tunnels = data.tunnels || []
    
    // Find HTTPS tunnel for port 3000 (frontend)
    const httpsTunnel = tunnels.find(t => 
      t.proto === 'https' && 
      t.config.addr.includes('3000')
    )
    
    if (httpsTunnel) {
      console.log('✅ Ngrok URL detected:', httpsTunnel.public_url)
      return httpsTunnel.public_url
    }
    
    // Fallback to any HTTPS tunnel
    const anyHttpsTunnel = tunnels.find(t => t.proto === 'https')
    if (anyHttpsTunnel) {
      console.log('✅ Ngrok URL detected (fallback):', anyHttpsTunnel.public_url)
      return anyHttpsTunnel.public_url
    }
    
    console.warn('No HTTPS ngrok tunnel found')
    return null
  } catch (error) {
    console.warn('Failed to detect ngrok URL:', error)
    return null
  }
}

/**
 * Check if ngrok is running
 */
export async function isNgrokRunning(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:4040/api/tunnels')
    return response.ok
  } catch {
    return false
  }
}

/**
 * Check if any tunnel is running (ngrok or Cloudflare Tunnel)
 */
export async function isAnyTunnelRunning(): Promise<boolean> {
  // First check ngrok
  const ngrokRunning = await isNgrokRunning()
  if (ngrokRunning) {
    return true
  }
  
  // Then check if we have a Cloudflare Tunnel URL
  const cloudflareUrl = await getCloudflareTunnelUrl()
  if (cloudflareUrl) {
    console.log('✅ Cloudflare Tunnel detected:', cloudflareUrl)
    return true
  }
  
  return false
}

/**
 * Get Cloudflare Tunnel URL from file
 */
async function getCloudflareTunnelUrl(): Promise<string | null> {
  try {
    // In browser, we can't read files directly, so we'll use a different approach
    if (typeof window !== 'undefined') {
      // Try to get the URL from localStorage first
      const savedUrl = localStorage.getItem('cloudflare-tunnel-url')
      if (savedUrl) {
        console.log('✅ Found Cloudflare Tunnel URL in localStorage:', savedUrl)
        return savedUrl
      }
      
      // Try to fetch it from an API endpoint
      try {
        const response = await fetch('/api/tunnel-url')
        if (response.ok) {
          const data = await response.text()
          const tunnelUrl = data.trim()
          console.log('✅ Found Cloudflare Tunnel URL from API:', tunnelUrl)
          return tunnelUrl
        }
      } catch (apiError) {
        console.log('API endpoint not available, trying localStorage only')
      }
    }
    
    return null
  } catch (error) {
    console.warn('Failed to get Cloudflare Tunnel URL:', error)
    return null
  }
}

/**
 * Get the public URL for sharing (ngrok, Cloudflare Tunnel, or localhost)
 */
export async function getPublicUrl(): Promise<string> {
  // First try ngrok
  const ngrokUrl = await getNgrokUrl()
  if (ngrokUrl) {
    return ngrokUrl
  }
  
  // Then try Cloudflare Tunnel
  const cloudflareUrl = await getCloudflareTunnelUrl()
  if (cloudflareUrl) {
    console.log('✅ Using Cloudflare Tunnel URL:', cloudflareUrl)
    return cloudflareUrl
  }
  
  // Fallback to localhost
  const localhostUrl = typeof window !== 'undefined' 
    ? window.location.origin 
    : 'http://localhost:3000'
  
  console.warn('Using localhost URL for sharing (Facebook may not work):', localhostUrl)
  return localhostUrl
}

/**
 * Get sharing URL for a poster
 */
export async function getPosterShareUrl(posterId: string): Promise<string> {
  const publicUrl = await getPublicUrl()
  return `${publicUrl}/poster/${posterId}`
}
