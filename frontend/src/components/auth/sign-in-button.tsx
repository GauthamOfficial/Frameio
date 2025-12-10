"use client"

import { Button, type ButtonProps } from "@/components/ui/button"
import { useAuthModal } from '@/contexts/auth-modal-context'

interface SignInButtonProps extends Omit<ButtonProps, 'onClick'> {
  children?: React.ReactNode
}

export function SignInButton({ children, className, variant = "ghost", size = "sm", ...props }: SignInButtonProps) {
  const { openSignIn } = useAuthModal()

  return (
    <Button onClick={openSignIn} variant={variant} size={size} className={className} {...props}>
      {children || "Sign In"}
    </Button>
  )
}
