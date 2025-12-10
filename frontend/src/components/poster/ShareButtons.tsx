'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { 
  Download, 
  Facebook, 
  Copy,
  CheckCircle
} from "lucide-react"

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

interface ShareButtonsProps {
  poster: PosterData
  pageUrl: string
}

export function ShareButtons({ poster, pageUrl }: ShareButtonsProps) {
  const [copiedItem, setCopiedItem] = useState<string | null>(null)

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItem(type)
      setTimeout(() => setCopiedItem(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const shareToFacebook = async () => {
    const shareText = poster.full_caption

    // Use the cloudinary_url (direct image URL) or public_url for sharing
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const shareableUrl = (poster as any).cloudinary_url || poster.public_url || poster.image_url
    const captionText = shareText || poster.caption || ''
    
    // Format hashtags as string
    const hashtagsArray = poster.hashtags || []
    const hashtagsStr = Array.isArray(hashtagsArray) 
      ? hashtagsArray.join(' ') 
      : (typeof hashtagsArray === 'string' ? hashtagsArray : '')
    
    // Combine caption and hashtags for the quote parameter
    const fullShareText = captionText 
      ? (hashtagsStr ? `${captionText}\n\n${hashtagsStr}` : captionText)
      : hashtagsStr
    
    // Ensure the URL is absolute and publicly accessible (must be Cloudinary URL)
    if (!shareableUrl || !shareableUrl.startsWith('http')) {
      console.error('❌ ERROR: Cannot share to Facebook - cloudinary_url is missing or not a public URL!')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      console.error('cloudinary_url:', (poster as any).cloudinary_url)
      console.error('public_url:', poster.public_url)
      console.error('image_url:', poster.image_url)
      alert('Unable to share to Facebook: Poster was not uploaded to Cloudinary. Please check backend logs.')
      return
    }
    
    const sharePageUrl = shareableUrl
    
    // Facebook sharer with Cloudinary image URL AND quote parameter containing caption + hashtags
    // The quote parameter will pre-fill the text field with caption and hashtags
    let shareLink = ''
    if (fullShareText) {
      shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}&quote=${encodeURIComponent(fullShareText)}`
    } else {
      shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}`
    }
    
    window.open(shareLink, '_blank')
  }

  const shareToClipboard = async () => {
    const shareText = `${poster.full_caption}\n\n${pageUrl}`
    await copyToClipboard(shareText, 'share')
  }

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = poster.image_url
    link.download = `poster_${poster.id}.png`
    link.click()
  }

  return (
    <>
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={shareToFacebook}
      >
        <Facebook className="w-4 h-4 mr-2 text-blue-600" />
        Share on Facebook
      </Button>
      
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={shareToClipboard}
      >
        {copiedItem === 'share' ? (
          <>
            <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
            Copied to Clipboard!
          </>
        ) : (
          <>
            <Copy className="w-4 h-4 mr-2" />
            Copy Link
          </>
        )}
      </Button>

      <div className="pt-4 border-t">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Download</h4>
        <Button 
          className="w-full"
          onClick={handleDownload}
        >
          <Download className="w-4 h-4 mr-2" />
          Download High Quality
        </Button>
      </div>
    </>
  )
}

