"use client"

import { useOrganization } from '@/contexts/organization-context'
import Link from 'next/link'
import { Shield, Lock } from 'lucide-react'

interface AdminNavLinkProps {
  href: string
  children: React.ReactNode
  className?: string
}

export default function AdminNavLink({ href, children, className = "" }: AdminNavLinkProps) {
  const { userRole } = useOrganization()

  // Only show admin links to admin users
  if (userRole !== 'Admin') {
    return null
  }

  return (
    <Link 
      href={href} 
      className={`flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors ${className}`}
    >
      <Shield className="h-4 w-4" />
      <span>{children}</span>
    </Link>
  )
}

// Component for showing admin-only content with a lock icon
export function AdminOnlyContent({ children, fallback }: { 
  children: React.ReactNode
  fallback?: React.ReactNode 
}) {
  const { userRole } = useOrganization()

  if (userRole !== 'Admin') {
    return fallback || (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <div className="text-center">
          <Lock className="h-8 w-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm">Admin access required</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
