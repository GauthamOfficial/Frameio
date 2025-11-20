"use client"

import { cn } from "@/lib/utils"
import { SidebarItem } from "./sidebar-item"
import { 
  LayoutDashboard,
  Users,
  Building2,
  CreditCard,
  BarChart3,
  Settings,
  HelpCircle
} from "lucide-react"

interface SidebarProps {
  items: Array<{
    href: string
    icon: any
    label: string
    badge?: string | number
  }>
  className?: string
}

export function Sidebar({ items, className }: SidebarProps) {
  return (
    <aside className={cn("w-64 bg-white border-r border-gray-200 h-screen flex-shrink-0", className)}>
      <div className="p-6 h-full flex flex-col">
        <div className="flex items-center space-x-2 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">F</span>
          </div>
          <span className="text-xl font-semibold text-gray-900">Frameio</span>
        </div>

        <nav className="space-y-2 flex-1">
          {items.map((item) => (
            <SidebarItem
              key={item.href}
              href={item.href}
              icon={item.icon}
              label={item.label}
              badge={item.badge}
            />
          ))}
        </nav>
      </div>
    </aside>
  )
}
