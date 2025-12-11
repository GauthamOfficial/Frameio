"use client"

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mail, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { sendVerificationEmail, setTokens, setUser } from '@/lib/auth'
import { useToastHelpers } from '@/components/common'
import { buildApiUrl } from '@/utils/api'

export default function CheckEmailPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { showSuccess, showError } = useToastHelpers()
  
  const email = searchParams?.get('email') || ''
  const token = searchParams?.get('token') || ''
  const [isResending, setIsResending] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error'>('pending')
  const [hasVerified, setHasVerified] = useState(false)

  const verifyEmail = useCallback(async (verificationToken: string) => {
    setIsVerifying(true)
    try {
      console.log('Verifying email with token:', verificationToken)
      const response = await fetch(buildApiUrl(`/api/users/auth/verify-email/${verificationToken}/`), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      console.log('Verification response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('Verification response data:', data)
        
        // Verify that user data includes is_verified: true
        if (data.user) {
          // Ensure is_verified is set to true
          const userData = {
            ...data.user,
            is_verified: true
          }
          setUser(userData)
          console.log('User data stored after verification:', userData)
        }
        
        // Automatically log in the user with the returned tokens
        if (data.access && data.refresh) {
          console.log('Tokens received, storing and redirecting...')
          // Store in localStorage for client-side access
          setTokens(data.access, data.refresh)
          
          // Use server-side API route to set cookies and redirect
          // This ensures cookies are set before redirect happens
          const redirectUrl = `/api/auth/set-tokens?access=${encodeURIComponent(data.access)}&refresh=${encodeURIComponent(data.refresh)}&redirect=/dashboard`
          console.log('Redirecting to:', redirectUrl)
          window.location.href = redirectUrl
        } else {
          console.warn('No tokens in response:', data)
          setVerificationStatus('success')
          showSuccess('Email verified successfully! You can now log in.')
          setTimeout(() => {
            router.push('/sign-in')
          }, 2000)
        }
      } else {
        const error = await response.json().catch(() => ({ error: 'Verification failed' }))
        console.error('Verification failed:', error)
        setVerificationStatus('error')
        showError(error.error || error.detail || 'Verification failed. The link may have expired.')
      }
    } catch (error) {
      console.error('Verification error:', error)
      setVerificationStatus('error')
      showError('An error occurred during verification. Please try again.')
    } finally {
      setIsVerifying(false)
    }
  }, [])

  // If token is provided, automatically verify
  useEffect(() => {
    if (token && verificationStatus === 'pending' && !hasVerified && !isVerifying) {
      console.log('Token detected, starting verification...')
      setHasVerified(true)
      verifyEmail(token)
    }
  }, [token, verificationStatus, hasVerified, isVerifying, verifyEmail])

  const handleResendEmail = async () => {
    if (!email) {
      showError('Email address not found. Please register again.')
      return
    }

    setIsResending(true)
    try {
      await sendVerificationEmail(email)
      showSuccess('Verification email sent! Please check your inbox.')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send verification email'
      showError(errorMessage)
    } finally {
      setIsResending(false)
    }
  }

  if (verificationStatus === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <CardTitle className="text-2xl">Email Verified!</CardTitle>
            <CardDescription>
              Your email has been successfully verified. Logging you in...
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              Your email has been verified. You should be automatically logged in. If not, please try signing in.
            </p>
            <Button onClick={() => window.location.href = '/dashboard'} className="w-full">
              Go to Dashboard
            </Button>
            <Button 
              onClick={() => router.push('/sign-in')} 
              variant="outline" 
              className="w-full"
            >
              Go to Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (verificationStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <CardTitle className="text-2xl">Verification Failed</CardTitle>
            <CardDescription>
              The verification link may have expired or is invalid.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {email && (
              <Button 
                onClick={handleResendEmail} 
                disabled={isResending}
                className="w-full"
                variant="outline"
              >
                {isResending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail className="mr-2 h-4 w-4" />
                    Resend Verification Email
                  </>
                )}
              </Button>
            )}
            <Button onClick={() => router.push('/sign-in')} className="w-full">
              Go to Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <Mail className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <CardTitle className="text-2xl">Check Your Email</CardTitle>
          <CardDescription>
            We've sent a verification link to
            {email && (
              <span className="font-semibold text-foreground"> {email}</span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-muted-foreground space-y-2">
            <p>Please check your email and click the verification link to activate your account.</p>
            <p className="text-xs">
              The link will expire in 24 hours. If you don't see the email, check your spam folder.
            </p>
          </div>

          {isVerifying ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="ml-2">Verifying your email...</span>
            </div>
          ) : (
            <>
              {email && (
                <Button 
                  onClick={handleResendEmail} 
                  disabled={isResending}
                  variant="outline"
                  className="w-full"
                >
                  {isResending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Resend Verification Email
                    </>
                  )}
                </Button>
              )}
              
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground text-center mb-4">
                  Already verified your email?
                </p>
                <Button 
                  onClick={() => router.push('/sign-in')} 
                  variant="ghost"
                  className="w-full"
                >
                  Go to Sign In
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

