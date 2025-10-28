'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { 
  Share2, 
  Download, 
  Facebook, 
  Twitter, 
  Instagram, 
  MessageCircle,
  Mail,
  Copy,
  CheckCircle
} from "lucide-react"

interface PosterData {
  id: string
  image_url: string
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

  const shareToSocialMedia = async (platform: string) => {
    const shareText = poster.full_caption
    const shareUrl = pageUrl

    let shareLink = ''
    
    switch (platform) {
      case 'facebook':
        try {
          // Import ngrok utility dynamically to avoid SSR issues
          const { isAnyTunnelRunning } = await import('@/utils/ngrok')
          
          // Check if any tunnel is running for Facebook sharing
          const tunnelRunning = await isAnyTunnelRunning()
          
          if (tunnelRunning) {
            // Use the provided pageUrl (which should be ngrok URL if available)
            shareLink = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`
          } else {
            // Fallback: Copy image URL and caption for manual sharing
            const imageUrl = poster.image_url.startsWith('http') 
              ? poster.image_url 
              : `http://localhost:8000${poster.image_url}`
            
            // Create a better formatted Facebook post
            const facebookText = `${shareText}\n\n🖼️ View the full poster: ${imageUrl}\n\n#AIPoster #Design #Innovation`
            await copyToClipboard(facebookText, 'facebook')
            
            // Show a better formatted alert
            const alertMessage = `📋 Copied to clipboard!\n\nPaste this into Facebook:\n\n${facebookText}\n\n💡 Tip: You can also download the image and upload it directly to Facebook for better results.`
            alert(alertMessage)
            return
          }
          
          window.open(
            shareLink,
            'facebook-share-dialog',
            'width=800,height=600,scrollbars=yes,resizable=yes'
          )
          return
        } catch (error) {
          console.error('Facebook sharing error:', error)
          // Fallback to clipboard
          const imageUrl = poster.image_url.startsWith('http') 
            ? poster.image_url 
            : `http://localhost:8000${poster.image_url}`
          
          // Create a better formatted Facebook post
          const facebookText = `${shareText}\n\n🖼️ View the full poster: ${imageUrl}\n\n#AIPoster #Design #Innovation`
          await copyToClipboard(facebookText, 'facebook')
          
          // Show a better formatted alert
          const alertMessage = `📋 Copied to clipboard!\n\nPaste this into Facebook:\n\n${facebookText}\n\n💡 Tip: You can also download the image and upload it directly to Facebook for better results.`
          alert(alertMessage)
          return
        }
      case 'twitter':
        shareLink = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`
        break
      case 'instagram':
        copyToClipboard(`${shareText}\n\n${shareUrl}`, 'instagram')
        return
      case 'whatsapp':
        shareLink = `https://wa.me/?text=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`
        break
      case 'email':
        shareLink = `mailto:?subject=${encodeURIComponent('Check out this AI-generated poster!')}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`
        break
      default:
        return
    }
    
    if (shareLink) {
      window.open(shareLink, '_blank')
    }
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
        onClick={() => shareToSocialMedia('facebook')}
      >
        <Facebook className="w-4 h-4 mr-2 text-blue-600" />
        Share on Facebook
      </Button>
      
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={() => shareToSocialMedia('twitter')}
      >
        <Twitter className="w-4 h-4 mr-2 text-blue-400" />
        Share on Twitter
      </Button>
      
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={() => shareToSocialMedia('instagram')}
      >
        <Instagram className="w-4 h-4 mr-2 text-pink-600" />
        {copiedItem === 'instagram' ? (
          <>
            <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
            Copied to Clipboard!
          </>
        ) : (
          <>
            <Copy className="w-4 h-4 mr-2" />
            Copy for Instagram
          </>
        )}
      </Button>
      
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={() => shareToSocialMedia('whatsapp')}
      >
        <MessageCircle className="w-4 h-4 mr-2 text-green-600" />
        Share on WhatsApp
      </Button>
      
      <Button 
        variant="outline" 
        className="w-full justify-start"
        onClick={() => shareToSocialMedia('email')}
      >
        <Mail className="w-4 h-4 mr-2 text-gray-600" />
        Share via Email
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

