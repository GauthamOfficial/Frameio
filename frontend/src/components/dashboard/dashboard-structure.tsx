"use client"

import { Sidebar } from "./sidebar"
import { TopNav } from "./top-nav"
import { Footer } from "@/components/layout/footer"
import { cn } from "@/lib/utils"

interface DashboardStructureProps {
  children: React.ReactNode
  className?: string
}

export function DashboardStructure({ children, className }: DashboardStructureProps) {
  return (
    <div className="min-h-screen bg-background fabric-texture flex flex-col min-w-[320px]">
      <Sidebar />
      <div className="md:ml-64 flex flex-col flex-1">
        <TopNav />
        <main className={cn("p-3 sm:p-4 md:p-6 flex-1", className)}>
          {children}
        </main>
        <Footer />
      </div>
    </div>
  )
}
