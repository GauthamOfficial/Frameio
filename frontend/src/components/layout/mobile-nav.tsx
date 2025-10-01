"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { SignInButton } from "@/components/auth/sign-in-button"
import { SignUpButton } from "@/components/auth/sign-up-button"
import { AuthUserButton } from "@/components/auth/user-button"
import { useUser } from '@clerk/nextjs'
import { cn } from "@/lib/utils"

interface MobileNavProps {
  className?: string
}

export function MobileNav({ className }: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false)
  const { isSignedIn } = useUser()

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
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center shine-gold glow-primary animate-shine">
                  <span className="text-primary-foreground font-bold text-lg">F</span>
                </div>
                <span className="text-xl font-bold text-gradient-primary">Frameio</span>
              </div>
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
            
            <nav className="flex-1 p-4 space-y-4">
              <a 
                href="#" 
                className="block text-lg text-foreground hover:text-accent transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Features
              </a>
              <a 
                href="#" 
                className="block text-lg text-foreground hover:text-accent transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Pricing
              </a>
              <a 
                href="#" 
                className="block text-lg text-foreground hover:text-accent transition-colors"
                onClick={() => setIsOpen(false)}
              >
                About
              </a>
            </nav>
            
            <div className="p-4 border-t border-border space-y-4">
              {isSignedIn ? (
                <div className="flex items-center justify-center">
                  <AuthUserButton />
                </div>
              ) : (
                <div className="space-y-2">
                  <SignInButton />
                  <SignUpButton />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
