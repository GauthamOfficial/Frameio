/**
 * Facebook Sharing Modal Component
 * Provides a better user experience for Facebook sharing fallback
 */

import React from 'react'

interface FacebookSharingModalProps {
  isOpen: boolean
  onClose: () => void
  content: string
  imageUrl: string
}

export function FacebookSharingModal({ isOpen, onClose, content, imageUrl }: FacebookSharingModalProps) {
  if (!isOpen) return null

  const handleDownloadImage = () => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = `poster_${Date.now()}.png`
    link.click()
  }

  const handleCopyContent = async () => {
    try {
      await navigator.clipboard.writeText(content)
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy content:', err)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">📱 Share to Facebook</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ×
          </button>
        </div>
        
        <div className="mb-4">
          <p className="text-gray-600 mb-3">
            Since no tunnel is running, Facebook can&apos;t access your poster page directly. 
            Here are two ways to share:
          </p>
        </div>

        <div className="space-y-3">
          <div className="border rounded-lg p-3 bg-gray-50">
            <h4 className="font-medium text-gray-800 mb-2">Option 1: Copy & Paste</h4>
            <p className="text-sm text-gray-600 mb-2">
              Copy the content below and paste it into Facebook:
            </p>
            <div className="bg-white border rounded p-2 text-sm font-mono text-gray-700 mb-2 max-h-32 overflow-y-auto">
              {content}
            </div>
            <button
              onClick={handleCopyContent}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
            >
              📋 Copy Content
            </button>
          </div>

          <div className="border rounded-lg p-3 bg-gray-50">
            <h4 className="font-medium text-gray-800 mb-2">Option 2: Download & Upload</h4>
            <p className="text-sm text-gray-600 mb-2">
              Download the image and upload it directly to Facebook for better results:
            </p>
            <button
              onClick={handleDownloadImage}
              className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 transition-colors"
            >
              📥 Download Image
            </button>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-gray-500">
            💡 <strong>Tip:</strong> For the best Facebook sharing experience, start a tunnel with: <code>node start-cloudflare-tunnel.js</code>
          </p>
        </div>
      </div>
    </div>
  )
}
