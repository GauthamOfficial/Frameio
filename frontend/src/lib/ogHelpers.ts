/**
 * Open Graph helper utilities for social media sharing
 */

/**
 * Truncate text to a maximum length, ensuring we don't cut words
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @param suffix - Suffix to add if truncated (default: '...')
 * @returns Truncated text
 */
export function truncateText(text: string, maxLength: number, suffix: string = '...'): string {
  if (!text || text.length <= maxLength) {
    return text
  }
  
  // Try to cut at word boundary
  const truncated = text.substring(0, maxLength - suffix.length)
  const lastSpace = truncated.lastIndexOf(' ')
  
  if (lastSpace > 0) {
    return truncated.substring(0, lastSpace) + suffix
  }
  
  return truncated + suffix
}

/**
 * Generate optimized Open Graph title from caption
 * Facebook recommends max 60 characters for og:title
 * @param caption - Poster caption
 * @param maxLength - Maximum length (default: 60)
 * @returns Optimized title
 */
export function generateOGTitle(caption: string | null | undefined, maxLength: number = 60): string {
  if (!caption) {
    return 'AI-Generated Poster'
  }
  
  return truncateText(caption, maxLength)
}

/**
 * Generate optimized Open Graph description from caption and hashtags
 * Facebook recommends max 200 characters for og:description
 * @param caption - Poster caption
 * @param hashtags - Array of hashtags
 * @param maxLength - Maximum length (default: 200)
 * @returns Optimized description
 */
export function generateOGDescription(
  caption: string | null | undefined,
  hashtags: string[] | null | undefined,
  maxLength: number = 200
): string {
  const parts: string[] = []
  
  if (caption) {
    parts.push(caption)
  }
  
  if (hashtags && hashtags.length > 0) {
    const hashtagsStr = hashtags.join(' ')
    parts.push(hashtagsStr)
  }
  
  const combined = parts.join(' ')
  
  if (!combined) {
    return 'Check out this AI-generated poster created with Framio!'
  }
  
  return truncateText(combined, maxLength)
}

/**
 * Ensure image URL is absolute
 * @param imageUrl - Image URL (can be relative or absolute)
 * @param baseUrl - Base URL for relative URLs (default: from env or localhost)
 * @returns Absolute URL
 */
export function ensureAbsoluteUrl(imageUrl: string, baseUrl?: string): string {
  if (!imageUrl) {
    return ''
  }
  
  // Already absolute
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  
  // Make absolute
  const base = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const cleanBase = base.replace(/\/$/, '')
  const cleanPath = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`
  
  return `${cleanBase}${cleanPath}`
}

/**
 * Build canonical poster page URL
 * @param posterId - Poster ID
 * @param baseUrl - Base URL (default: from env or localhost:3000)
 * @returns Canonical URL
 */
export function buildPosterPageUrl(posterId: string, baseUrl?: string): string {
  const base = baseUrl || process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
  const cleanBase = base.replace(/\/$/, '')
  return `${cleanBase}/poster/${posterId}`
}







