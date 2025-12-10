"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthModal } from '@/contexts/auth-modal-context'

export default function SignInPage() {
  const router = useRouter()
  const { openSignIn } = useAuthModal()

  useEffect(() => {
    // Open the modal when the page is accessed directly
    openSignIn()
    
    // Redirect to home page so the modal shows over the home page
    const timer = setTimeout(() => {
      router.replace('/')
    }, 100)
    
    return () => clearTimeout(timer)
  }, [openSignIn, router])

  // Return a minimal loading state while redirecting
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="animate-pulse text-muted-foreground">Loading...</div>
    </div>
  )
}
