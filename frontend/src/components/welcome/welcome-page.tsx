"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { SignInButton as ClerkSignInButton, SignUpButton as ClerkSignUpButton, useUser } from '@clerk/nextjs'
import { MobileNav } from "@/components/welcome/mobile-nav"
import { Footer } from "@/components/layout/footer"
import { Logo } from "@/components/common/logo"
import { cn } from "@/lib/utils"
import { ArrowRight, Palette, Calendar, BarChart3 } from "lucide-react"
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from "next/link"

interface WelcomePageProps {
  className?: string
}

export function WelcomePage({ className }: WelcomePageProps) {
  const { isSignedIn, isLoaded } = useUser()
  const router = useRouter()

  // Redirect to dashboard if user is already signed in (only on initial load)
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      // Small delay to allow navigation from logo click
      const timer = setTimeout(() => {
        router.push('/dashboard')
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [isLoaded, isSignedIn, router])

  // Show loading while checking auth status
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
          <p className="text-muted-foreground">Loading Frameio...</p>
          <p className="text-sm text-muted-foreground mt-2">Initializing authentication...</p>
        </div>
      </div>
    )
  }

  // Don't render if user is signed in (will redirect)
  if (isSignedIn) {
    return null
  }

  return (
    <div className={cn("min-h-screen bg-background fabric-texture", className)}>
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Logo href="/" />

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link
                href="/"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Home
              </Link>
              <Link
                href="/about"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Contact Us
              </Link>
            </nav>

            {/* Auth Buttons */}
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-4">
                <ClerkSignInButton mode="modal" fallbackRedirectUrl="/dashboard">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </ClerkSignInButton>
                <ClerkSignUpButton mode="modal" fallbackRedirectUrl="/dashboard">
                  <Button size="sm">
                    Get Started
                  </Button>
                </ClerkSignUpButton>
              </div>
              <MobileNav />
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          {/* Hero Content */}
          <div className="mb-12">
            <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
              Where <span className="text-[#8B2635]">Textile</span> Designs Become Stunning Posters
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Frameio helps you create beautiful, professional posters that highlight your fabrics, styles, and seasonal collections instantly.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <ClerkSignUpButton mode="modal" fallbackRedirectUrl="/dashboard">
                <Button size="lg" className="text-lg">
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </ClerkSignUpButton>
              <ClerkSignInButton mode="modal" fallbackRedirectUrl="/dashboard">
                <Button variant="outline" size="lg" className="text-lg">
                  Login
                </Button>
              </ClerkSignInButton>
            </div>
            
          </div>

          {/* Hero Illustration Placeholder */}
          <div className="mb-16">
            <Card className="textile-hover textile-shadow max-w-4xl mx-auto border-2 border-[#8B2635] rounded-xl bg-[#F5F1EB]">
              <CardContent className="p-8 relative overflow-hidden aspect-video">
                {/* Floating Images */}
                <div className="absolute inset-0 pointer-events-none">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/Floating IMAGES/1.png" 
                    alt="Floating design 1" 
                    className="absolute w-[50%] h-[50%] md:w-[40%] md:h-[40%] object-contain animate-float-1"
                    style={{ top: '5%', left: '-5%' }}
                  />
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/Floating IMAGES/2.png" 
                    alt="Floating design 2" 
                    className="absolute w-[50%] h-[50%] md:w-[40%] md:h-[40%] object-contain animate-float-2"
                    style={{ top: '5%', right: '-5%' }}
                  />
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/Floating IMAGES/3.png" 
                    alt="Floating design 3" 
                    className="absolute w-[50%] h-[50%] md:w-[40%] md:h-[40%] object-contain animate-float-3"
                    style={{ bottom: '3%', left: '-5%' }}
                  />
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/Floating IMAGES/4.png" 
                    alt="Floating design 4" 
                    className="absolute w-[50%] h-[50%] md:w-[40%] md:h-[40%] object-contain animate-float-4"
                    style={{ bottom: '0.5%', right: '-5%' }}
                  />
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/Floating IMAGES/5.png" 
                    alt="Floating design 5" 
                    className="absolute w-[75%] h-[75%] md:w-[70%] md:h-[70%] object-contain animate-float-5"
                    style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <Card className="textile-hover textile-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-chart-1 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <Palette className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">AI Design Generation</h3>
                <p className="text-muted-foreground">
                  Create stunning textile designs with AI-powered tools that understand your brand and style.
                </p>
              </CardContent>
            </Card>
            
            <Card className="textile-hover textile-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-chart-2 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Smart Scheduling</h3>
                <p className="text-muted-foreground">
                  Plan and schedule your marketing posts across all platforms with optimal timing.
                </p>
              </CardContent>
            </Card>
            
            <Card className="textile-hover textile-shadow">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-chart-3 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Analytics & Insights</h3>
                <p className="text-muted-foreground">
                  Track performance and get insights to optimize your marketing strategy.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* CTA Section */}
          <div className="bg-textile-gradient rounded-lg p-8 textile-shadow">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Ready to Transform Your Textile Business?
            </h2>
            <p className="text-lg text-muted-foreground mb-6">
              Join hundreds of textile shops already using Frameio to create stunning marketing materials.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <ClerkSignUpButton mode="modal" fallbackRedirectUrl="/dashboard">
                <Button size="lg" className="bg-textile-accent hover:bg-textile-accent/90">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </ClerkSignUpButton>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
