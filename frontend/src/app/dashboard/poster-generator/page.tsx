"use client"

import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { LoadingSpinner } from '@/components/common'

// Lazy load the Enhanced PosterGenerator component with AI integration and business branding
const PosterGenerator = dynamic(() => import('@/components/lazy/enhanced-poster-generator-with-branding'), {
  loading: () => (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" text="Loading AI-Powered Poster Generator with Business Branding..." />
    </div>
  ),
  ssr: false
})

export default function PosterGeneratorPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading AI-Powered Poster Generator with Business Branding..." />
      </div>
    }>
      <PosterGenerator />
    </Suspense>
  )
}
