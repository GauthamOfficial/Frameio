"use client"

import { Suspense } from 'react'
import { DashboardErrorBoundary } from '@/components/common/error-boundary'
import AIPostGenerator from '@/components/lazy/ai-post-generator'
import { Loader2 } from 'lucide-react'

export default function AIPostGeneratorPage() {
  return (
    <DashboardErrorBoundary>
      <Suspense fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      }>
        <AIPostGenerator />
      </Suspense>
    </DashboardErrorBoundary>
  )
}
