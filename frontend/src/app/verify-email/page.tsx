"use client"

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mail, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { sendVerificationEmail, verifyEmail, setTokens, setUser } from '@/lib/auth'
import { useToastHelpers } from '@/components/common'

function VerifyEmailContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { showSuccess, showError } = useToastHelpers()
  
  const token = searchParams?.get('token')
  const email = searchParams?.get('email')
  
  const [status, setStatus] = useState<'pending' | 'verifying' | 'success' | 'error'>('pending')
  const [isResending, setIsResending] = useState(false)
  const [userEmail, setUserEmail] = useState(email || '')

  const handleVerify = useCallback(async (verificationToken: string) => {
    setStatus('verifying')
    
    try {
      const result = await verifyEmail(verificationToken)
      
      // If tokens are returned, use server-side route to set cookies and redirect
      if (result.access && result.refresh) {
        // Store in localStorage for client-side access
        setTokens(result.access, result.refresh)
        
        // Store user data with is_verified set to true
        if (result.user) {
          const userData = {
            ...result.user,
            is_verified: true
          }
          setUser(userData)
          console.log('User data stored after verification:', userData)
        }
        
        setStatus('success')
        showSuccess('Email verified successfully! Logging you in...')
        
        // Use server-side API route to set cookies and redirect
        // This ensures cookies are set before redirect happens
        const redirectUrl = `/api/auth/set-tokens?access=${encodeURIComponent(result.access)}&refresh=${encodeURIComponent(result.refresh)}&redirect=/dashboard`
        window.location.href = redirectUrl
      } else {
        setStatus('success')
        showSuccess('Email verified successfully! You can now log in.')
        setTimeout(() => {
          router.push('/sign-in')
        }, 2000)
      }
    } catch (error) {
      setStatus('error')
      const errorMessage = error instanceof Error ? error.message : 'Failed to verify email'
      showError(errorMessage)
    }
  }, [router, showError, showSuccess])

  // Auto-verify if token is provided
  useEffect(() => {
    if (token && status === 'pending') {
      handleVerify(token)
    }
  }, [token, status, handleVerify])

  const handleResendEmail = async () => {
    if (!userEmail) {
      showError('Please enter your email address')
      return
    }

    setIsResending(true)
    
    try {
      await sendVerificationEmail(userEmail)
      showSuccess('Verification email sent! Please check your inbox.')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send verification email'
      showError(errorMessage)
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            {status === 'success' ? (
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            ) : status === 'error' ? (
              <AlertCircle className="h-8 w-8 text-red-600" />
            ) : status === 'verifying' ? (
              <Loader2 className="h-8 w-8 text-primary animate-spin" />
            ) : (
              <Mail className="h-8 w-8 text-primary" />
            )}
          </div>
          <CardTitle className="text-2xl">
            {status === 'success' 
              ? 'Email Verified!' 
              : status === 'error'
              ? 'Verification Failed'
              : status === 'verifying'
              ? 'Verifying...'
              : 'Check Your Email'}
          </CardTitle>
          <CardDescription>
            {status === 'success'
              ? 'Your email has been verified successfully. Logging you in...'
              : status === 'error'
              ? 'The verification link is invalid or has expired. Please request a new one.'
              : status === 'verifying'
              ? 'Please wait while we verify your email...'
              : 'We&apos;ve sent a verification link to your email address. Please click the link to verify your account.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {status === 'pending' && (
            <>
              <div className="rounded-lg bg-muted p-4 text-sm">
                <p className="mb-2 font-medium">Didn&apos;t receive the email?</p>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground mb-4">
                  <li>Check your spam/junk folder</li>
                  <li>Make sure you entered the correct email address</li>
                  <li>Wait a few minutes and try again</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Resend verification email to:
                </label>
                <input
                  id="email"
                  type="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
                <Button
                  onClick={handleResendEmail}
                  disabled={isResending || !userEmail}
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
              </div>
              
              <Button
                variant="outline"
                onClick={() => router.push('/sign-in')}
                className="w-full"
              >
                Back to Sign In
              </Button>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
                <p className="font-medium mb-2">Verification failed</p>
                <p>The verification link may have expired or is invalid. Please request a new verification email.</p>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="email-error" className="text-sm font-medium">
                  Enter your email to resend verification:
                </label>
                <input
                  id="email-error"
                  type="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
                <Button
                  onClick={handleResendEmail}
                  disabled={isResending || !userEmail}
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
              </div>
              
              <Button
                variant="outline"
                onClick={() => router.push('/sign-in')}
                className="w-full"
              >
                Back to Sign In
              </Button>
            </>
          )}
          
          {status === 'success' && (
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">
                You will be redirected to the dashboard shortly...
              </p>
              <Button
                onClick={() => window.location.href = '/dashboard'}
                className="w-full"
              >
                Go to Dashboard
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailContent />
    </Suspense>
  )
}

