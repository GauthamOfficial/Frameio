"use client"

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Lock, CheckCircle2, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react'
import { buildApiUrl } from '@/utils/api'
import { useToastHelpers } from '@/components/common'
import Link from 'next/link'

function ResetPasswordContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { showSuccess, showError } = useToastHelpers()
  
  const token = searchParams?.get('token')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(true)
  const [tokenValid, setTokenValid] = useState(false)
  const [userEmail, setUserEmail] = useState('')
  const [success, setSuccess] = useState(false)

  const verifyToken = useCallback(async (resetToken: string) => {
    try {
      const response = await fetch(buildApiUrl(`/api/users/auth/verify-reset-token/${resetToken}/`), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Invalid or expired token')
      }

      setTokenValid(true)
      setUserEmail(data.email || '')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Invalid or expired token'
      showError(errorMessage)
      setTokenValid(false)
    } finally {
      setVerifying(false)
    }
  }, [showError])

  // Verify token on mount
  useEffect(() => {
    if (token) {
      verifyToken(token)
    } else {
      setVerifying(false)
      setTokenValid(false)
    }
  }, [token, verifyToken])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!password) {
      showError('Please enter a new password')
      return
    }

    if (password !== confirmPassword) {
      showError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      showError('Password must be at least 8 characters long')
      return
    }

    if (!token) {
      showError('Invalid reset token')
      return
    }

    setLoading(true)
    
    try {
      const response = await fetch(buildApiUrl(`/api/users/auth/reset-password/${token}/`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password,
          confirm_password: confirmPassword,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.details?.[0] || 'Failed to reset password')
      }

      setSuccess(true)
      showSuccess('Password reset successfully! Redirecting to sign in...')
      
      setTimeout(() => {
        router.push('/sign-in')
      }, 2000)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to reset password'
      showError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center space-y-4 py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Verifying reset token...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!tokenValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <CardTitle className="text-2xl">Invalid or Expired Link</CardTitle>
            <CardDescription>
              This password reset link is invalid or has expired
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              Password reset links expire after 1 hour. Please request a new one.
            </p>
            <div className="space-y-2">
              <Button
                className="w-full"
                onClick={() => router.push('/forgot-password')}
              >
                Request New Reset Link
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push('/sign-in')}
              >
                Back to Sign In
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            </div>
            <CardTitle className="text-2xl">Password Reset Successful</CardTitle>
            <CardDescription>
              Your password has been reset successfully
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground text-center mb-4">
              You can now sign in with your new password.
            </p>
            <Button
              className="w-full"
              onClick={() => router.push('/sign-in')}
            >
              Go to Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Lock className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">Reset Your Password</CardTitle>
          <CardDescription>
            {userEmail && `Enter a new password for ${userEmail}`}
            {!userEmail && 'Enter your new password'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter new password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                  autoComplete="new-password"
                  className="pr-10"
                  minLength={8}
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
            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={loading}
                  autoComplete="new-password"
                  className="pr-10"
                  minLength={8}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={loading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Resetting Password...
                </>
              ) : (
                <>
                  <Lock className="mr-2 h-4 w-4" />
                  Reset Password
                </>
              )}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <Link
              href="/sign-in"
              className="text-sm text-muted-foreground hover:text-primary"
            >
              Back to Sign In
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordContent />
    </Suspense>
  )
}

