"use client"

import React, { createContext, useContext, useState } from 'react'

interface AuthModalContextType {
  showSignIn: boolean
  showSignUp: boolean
  openSignIn: () => void
  openSignUp: () => void
  closeSignIn: () => void
  closeSignUp: () => void
  switchToSignUp: () => void
  switchToSignIn: () => void
}

const AuthModalContext = createContext<AuthModalContextType | undefined>(undefined)

export function AuthModalProvider({ children }: { children: React.ReactNode }) {
  const [showSignIn, setShowSignIn] = useState(false)
  const [showSignUp, setShowSignUp] = useState(false)

  const openSignIn = () => {
    setShowSignUp(false)
    setShowSignIn(true)
  }

  const openSignUp = () => {
    setShowSignIn(false)
    setShowSignUp(true)
  }

  const closeSignIn = () => setShowSignIn(false)
  const closeSignUp = () => setShowSignUp(false)

  const switchToSignUp = () => {
    setShowSignIn(false)
    setShowSignUp(true)
  }

  const switchToSignIn = () => {
    setShowSignUp(false)
    setShowSignIn(true)
  }

  return (
    <AuthModalContext.Provider
      value={{
        showSignIn,
        showSignUp,
        openSignIn,
        openSignUp,
        closeSignIn,
        closeSignUp,
        switchToSignUp,
        switchToSignIn,
      }}
    >
      {children}
    </AuthModalContext.Provider>
  )
}

export function useAuthModal() {
  const context = useContext(AuthModalContext)
  if (!context) {
    throw new Error('useAuthModal must be used within AuthModalProvider')
  }
  return context
}

