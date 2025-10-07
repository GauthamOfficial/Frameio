"use client"

import dynamic from 'next/dynamic'
import { LoadingSpinner } from '@/components/common'

// Lazy load the Enhanced PosterGenerator component with AI integration
const PosterGenerator = dynamic(() => import('@/components/lazy/enhanced-poster-generator'), {
  loading: () => (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" text="Loading AI-Powered Poster Generator..." />
    </div>
  ),
  ssr: false
})

export default function PosterGeneratorPage() {
  return <PosterGenerator />
}
