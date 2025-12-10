"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthModal } from '@/contexts/auth-modal-context'

export default function SignUpPage() {
  const router = useRouter()
  const { openSignUp } = useAuthModal()

  useEffect(() => {
    // Open the modal when the page is accessed directly
    openSignUp()
    
    // Redirect to home page so the modal shows over the home page
    const timer = setTimeout(() => {
      router.replace('/')
    }, 100)
    
    return () => clearTimeout(timer)
  }, [openSignUp, router])

  // Return a minimal loading state while redirecting
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="animate-pulse text-muted-foreground">Loading...</div>
    </div>
  )
}
