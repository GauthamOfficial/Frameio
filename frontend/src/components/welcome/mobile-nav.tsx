"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { SignInButton as ClerkSignInButton, SignUpButton as ClerkSignUpButton, useUser } from '@clerk/nextjs'
import { Menu, X } from "lucide-react"
import { Logo } from "@/components/common/logo"
import { cn } from "@/lib/utils"

interface MobileNavProps {
  className?: string
}

export function MobileNav({ className }: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false)
  const { isSignedIn, isLoaded } = useUser()

  // Don't render auth buttons if user is signed in
  if (isLoaded && isSignedIn) {
    return null
  }

  return (
    <div className={cn("md:hidden", className)}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="relative z-50"
      >
        <span className="sr-only">Toggle menu</span>
        <div className="w-6 h-6 flex flex-col justify-center items-center">
          <span className={cn("w-5 h-0.5 bg-current transition-all duration-300", isOpen ? "rotate-45 translate-y-1" : "")} />
          <span className={cn("w-5 h-0.5 bg-current transition-all duration-300", isOpen ? "opacity-0" : "mt-1")} />
          <span className={cn("w-5 h-0.5 bg-current transition-all duration-300", isOpen ? "-rotate-45 -translate-y-1" : "mt-1")} />
        </div>
      </Button>

      {isOpen && (
        <div className="fixed inset-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex flex-col h-full">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <Logo href="/" />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
              >
                <span className="sr-only">Close menu</span>
                <div className="w-6 h-6 flex flex-col justify-center items-center">
                  <span className="w-5 h-0.5 bg-current rotate-45" />
                  <span className="w-5 h-0.5 bg-current -rotate-45 -translate-y-0.5" />
                </div>
              </Button>
            </div>
            
            <div className="flex-1 p-4 flex flex-col justify-center space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-foreground mb-2">Welcome to Frameio</h2>
                <p className="text-muted-foreground mb-6">
                  AI-Powered Marketing Assets for Textile Shops
                </p>
              </div>
              
              <div className="space-y-4">
                <ClerkSignUpButton mode="modal" afterSignUpUrl="/dashboard">
                  <Button className="w-full" size="lg">
                    Get Started
                  </Button>
                </ClerkSignUpButton>
                <ClerkSignInButton mode="modal" afterSignInUrl="/dashboard">
                  <Button variant="outline" className="w-full" size="lg">
                    Login
                  </Button>
                </ClerkSignInButton>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
