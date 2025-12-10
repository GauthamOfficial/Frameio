"use client"

import { Button, type ButtonProps } from '@/components/ui/button'
import { useAuthModal } from '@/contexts/auth-modal-context'

interface SignUpButtonProps extends Omit<ButtonProps, 'onClick'> {
  children?: React.ReactNode
}

export function SignUpButton({ children, className, variant = "default", size = "sm", ...props }: SignUpButtonProps) {
  const { openSignUp } = useAuthModal()

  return (
    <Button onClick={openSignUp} variant={variant} size={size} className={className} {...props}>
      {children || "Sign Up"}
    </Button>
  )
}
