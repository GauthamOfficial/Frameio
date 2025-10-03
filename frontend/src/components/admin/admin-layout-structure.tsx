"use client"

import { Sidebar } from "@/components/common/sidebar"
import { Navbar } from "@/components/common/navbar"
import { 
  LayoutDashboard,
  Users,
  Building2,
  CreditCard,
  BarChart3,
  Settings
} from "lucide-react"

interface AdminLayoutStructureProps {
  children: React.ReactNode
}

export function AdminLayoutStructure({ children }: AdminLayoutStructureProps) {
  const adminNavItems = [
    {
      href: "/admin",
      icon: LayoutDashboard,
      label: "Overview",
    },
    {
      href: "/admin/users",
      icon: Users,
      label: "User Management",
      badge: "12"
    },
    {
      href: "/admin/organization",
      icon: Building2,
      label: "Organization",
    },
    {
      href: "/admin/billing",
      icon: CreditCard,
      label: "Billing",
    },
    {
      href: "/admin/analytics",
      icon: BarChart3,
      label: "Analytics",
    },
    {
      href: "/admin/settings",
      icon: Settings,
      label: "Settings",
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar items={adminNavItems} />
      <div className="flex-1 flex flex-col">
        <Navbar title="Admin Panel" />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
