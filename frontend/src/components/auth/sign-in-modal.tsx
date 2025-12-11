"use client"

import { useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { login } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { useToastHelpers } from '@/components/common'
import { useAuthModal } from '@/contexts/auth-modal-context'
import { Eye, EyeOff } from 'lucide-react'

export function SignInModal() {
  const searchParams = useSearchParams()
  const { showSuccess, showError } = useToastHelpers()
  const { showSignIn, closeSignIn, switchToSignUp } = useAuthModal()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleForgotPassword = () => {
    closeSignIn()
    // Use window.location for a hard navigation to ensure we leave the modal context
    window.location.href = '/forgot-password'
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await login(email, password)
      showSuccess('Successfully signed in!')
      closeSignIn()
      
      // Reset form
      setEmail('')
      setPassword('')
      
      // Redirect to dashboard or the redirect_url if provided
      const redirectUrl = searchParams?.get('redirect_url') || '/dashboard'
      
      // Use window.location for a hard redirect to ensure middleware sees the cookie
      setTimeout(() => {
        window.location.href = redirectUrl
      }, 150)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to sign in'
      
      // Check if error is about email verification
      if (errorMessage.toLowerCase().includes('email not verified') || 
          errorMessage.toLowerCase().includes('verify your email')) {
        // Show error and offer to resend verification email
        showError('Please verify your email address before logging in.')
        // Optionally redirect to verify email page
        setTimeout(() => {
          window.location.href = `/verify-email?email=${encodeURIComponent(email)}`
        }, 2000)
      } else {
        showError(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      closeSignIn()
      setEmail('')
      setPassword('')
    }
  }

  return (
    <Dialog open={showSignIn} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Sign In</DialogTitle>
          <DialogDescription>
            Enter your credentials to access your account
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="modal-email">Email</Label>
            <Input
              id="modal-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              autoComplete="email"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="modal-password">Password</Label>
            <div className="relative">
              <Input
                id="modal-password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                autoComplete="current-password"
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        <div className="mt-4 space-y-2">
          <div className="text-center text-sm">
            <button
              type="button"
              onClick={handleForgotPassword}
              className="text-primary hover:underline font-medium"
              disabled={loading}
            >
              Forgot password?
            </button>
          </div>
          <div className="text-center text-sm">
            <span className="text-muted-foreground">Don&apos;t have an account? </span>
            <button
              type="button"
              onClick={switchToSignUp}
              className="text-primary hover:underline font-medium"
              disabled={loading}
            >
              Sign up
            </button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

