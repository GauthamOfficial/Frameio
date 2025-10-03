"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface SidebarItemProps {
  href: string
  icon: LucideIcon
  label: string
  badge?: string | number
  isActive?: boolean
  className?: string
}

export function SidebarItem({ 
  href, 
  icon: Icon, 
  label, 
  badge, 
  isActive = false,
  className 
}: SidebarItemProps) {
  const pathname = usePathname()
  const isCurrentPath = pathname === href || isActive

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors",
        isCurrentPath
          ? "bg-blue-50 text-blue-700 border-r-2 border-blue-700"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900",
        className
      )}
    >
      <div className="flex items-center space-x-3">
        <Icon className="w-5 h-5" />
        <span>{label}</span>
      </div>
      {badge && (
        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
          {badge}
        </span>
      )}
    </Link>
  )
}
