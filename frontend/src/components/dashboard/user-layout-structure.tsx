"use client"

import { Sidebar } from "@/components/common/sidebar"
import { Navbar } from "@/components/common/navbar"
import { 
  LayoutDashboard,
  Image,
  FolderOpen,
  Palette,
  Calendar,
  Settings
} from "lucide-react"

interface UserLayoutStructureProps {
  children: React.ReactNode
}

export function UserLayoutStructure({ children }: UserLayoutStructureProps) {
  const userNavItems = [
    {
      href: "/dashboard",
      icon: LayoutDashboard,
      label: "Overview",
    },
    {
      href: "/dashboard/poster-generator",
      icon: Image,
      label: "Poster Generator",
    },
    {
      href: "/dashboard/catalog-builder",
      icon: FolderOpen,
      label: "Catalog Builder",
    },
    {
      href: "/dashboard/branding-kit",
      icon: Palette,
      label: "Branding Kit",
    },
    {
      href: "/dashboard/scheduler",
      icon: Calendar,
      label: "Scheduler",
    },
    {
      href: "/dashboard/settings",
      icon: Settings,
      label: "Settings",
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar items={userNavItems} />
      <div className="flex-1 flex flex-col">
        <Navbar title="Dashboard" />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
