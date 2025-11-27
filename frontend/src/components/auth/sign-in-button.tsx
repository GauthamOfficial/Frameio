"use client"

import { SignInButton as ClerkSignInButton } from '@clerk/nextjs'
import { Button } from "@/components/ui/button"

interface SignInButtonProps {
  children?: React.ReactNode
  className?: string
}

export function SignInButton({ children, className }: SignInButtonProps) {
  if (children) {
    return (
      <ClerkSignInButton mode="modal" fallbackRedirectUrl="/dashboard">
        {children}
      </ClerkSignInButton>
    )
  }

  return (
    <ClerkSignInButton mode="modal" fallbackRedirectUrl="/dashboard">
      <Button variant="ghost" size="sm" className={className}>
        Sign In
      </Button>
    </ClerkSignInButton>
  )
}
