"use client"

import { useApp } from "@/contexts/app-context"
import { GlobalLoading } from "@/components/common"

interface AppLayoutWrapperProps {
  children: React.ReactNode
}

export function AppLayoutWrapper({ children }: AppLayoutWrapperProps) {
  const { isGlobalLoading } = useApp()
  
  return (
    <>
      {children}
      <GlobalLoading isVisible={isGlobalLoading} />
    </>
  )
}
