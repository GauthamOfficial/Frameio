"use client"

import { Suspense } from "react"
import { useApp } from "@/contexts/app-context"
import { GlobalLoading } from "@/components/common"
import { SignInModal } from "@/components/auth/sign-in-modal"
import { SignUpModal } from "@/components/auth/sign-up-modal"

interface AppLayoutWrapperProps {
  children: React.ReactNode
}

export function AppLayoutWrapper({ children }: AppLayoutWrapperProps) {
  const { isGlobalLoading } = useApp()
  
  return (
    <>
      {children}
      <GlobalLoading isVisible={isGlobalLoading} />
      <Suspense fallback={null}>
        <SignInModal />
      </Suspense>
      <SignUpModal />
    </>
  )
}
