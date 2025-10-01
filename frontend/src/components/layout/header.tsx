"use client"

import { useUser } from '@clerk/nextjs'
import { Button } from "@/components/ui/button"
import { SignInButton } from "@/components/auth/sign-in-button"
import { SignUpButton } from "@/components/auth/sign-up-button"
import { AuthUserButton } from "@/components/auth/user-button"
import { MobileNav } from "@/components/layout/mobile-nav"
import { cn } from "@/lib/utils"

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps) {
  const { isSignedIn } = useUser()

  return (
    <header className={cn("border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60", className)}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center shine-gold glow-primary animate-shine">
              <span className="text-primary-foreground font-bold text-lg">F</span>
            </div>
            <span className="text-xl font-bold text-gradient-primary">Frameio</span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-6">
            <a 
              href="#" 
              className="text-foreground hover:text-accent transition-colors"
            >
              Features
            </a>
            <a 
              href="#" 
              className="text-foreground hover:text-accent transition-colors"
            >
              Pricing
            </a>
            <a 
              href="#" 
              className="text-foreground hover:text-accent transition-colors"
            >
              About
            </a>
          </nav>

          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-4">
              {isSignedIn ? (
                <AuthUserButton />
              ) : (
                <>
                  <SignInButton />
                  <SignUpButton />
                </>
              )}
            </div>
            <MobileNav />
          </div>
        </div>
      </div>
    </header>
  )
}
