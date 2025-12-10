"use client"

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { login } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { useToastHelpers } from '@/components/common'
import { useAuthModal } from '@/contexts/auth-modal-context'

export function SignInModal() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { showSuccess, showError } = useToastHelpers()
  const { showSignIn, closeSignIn, switchToSignUp } = useAuthModal()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

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
      showError(errorMessage)
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
            <Input
              id="modal-password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              autoComplete="current-password"
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        <div className="mt-4 text-center text-sm">
          <span className="text-muted-foreground">Don't have an account? </span>
          <button
            type="button"
            onClick={switchToSignUp}
            className="text-primary hover:underline font-medium"
            disabled={loading}
          >
            Sign up
          </button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

