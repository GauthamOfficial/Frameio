"use client"

import { useRouter } from 'next/navigation'
import { Button, type ButtonProps } from "@/components/ui/button"

interface SignInButtonProps extends Omit<ButtonProps, 'onClick'> {
  children?: React.ReactNode
}

export function SignInButton({ children, className, variant = "ghost", size = "sm", ...props }: SignInButtonProps) {
  const router = useRouter()

  const handleClick = () => {
    router.push('/sign-in')
  }

  return (
    <Button onClick={handleClick} variant={variant} size={size} className={className} {...props}>
      {children || "Sign In"}
    </Button>
  )
}
