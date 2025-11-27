"use client"

import { SignUpButton as ClerkSignUpButton } from '@clerk/nextjs'
import { Button } from "@/components/ui/button"

interface SignUpButtonProps {
  children?: React.ReactNode
  className?: string
}

export function SignUpButton({ children, className }: SignUpButtonProps) {
  if (children) {
    return (
      <ClerkSignUpButton mode="modal" fallbackRedirectUrl="/dashboard">
        {children}
      </ClerkSignUpButton>
    )
  }

  return (
    <ClerkSignUpButton mode="modal" fallbackRedirectUrl="/dashboard">
      <Button size="sm" className={className}>
        Get Started
      </Button>
    </ClerkSignUpButton>
  )
}
