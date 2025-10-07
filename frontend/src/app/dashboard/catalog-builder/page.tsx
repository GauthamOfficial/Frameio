"use client"

import dynamic from 'next/dynamic'
import { LoadingSpinner } from '@/components/common'

// Lazy load the CatalogBuilder component
const CatalogBuilder = dynamic(() => import('@/components/lazy/catalog-builder'), {
  loading: () => (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" text="Loading Catalog Builder..." />
    </div>
  ),
  ssr: false
})

export default function CatalogBuilderPage() {
  return <CatalogBuilder />
}
