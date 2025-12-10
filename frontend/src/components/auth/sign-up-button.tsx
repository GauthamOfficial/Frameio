"use client"

import { useRouter } from 'next/navigation'
import { Button, type ButtonProps } from '@/components/ui/button'

interface SignUpButtonProps extends Omit<ButtonProps, 'onClick'> {
  children?: React.ReactNode
}

export function SignUpButton({ children, className, variant = "default", size = "sm", ...props }: SignUpButtonProps) {
  const router = useRouter()

  const handleClick = () => {
    router.push('/sign-up')
  }

  return (
    <Button onClick={handleClick} variant={variant} size={size} className={className} {...props}>
      {children || "Sign Up"}
    </Button>
  )
}
