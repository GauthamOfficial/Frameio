"use client"

import dynamic from 'next/dynamic'
import { LoadingSpinner } from '@/components/common'

// Lazy load the PosterGenerator component
const PosterGenerator = dynamic(() => import('@/components/lazy/poster-generator'), {
  loading: () => (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" text="Loading Poster Generator..." />
    </div>
  ),
  ssr: false
})

export default function PosterGeneratorPage() {
  return <PosterGenerator />
}
