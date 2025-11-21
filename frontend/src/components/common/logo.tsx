import Image from "next/image"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface LogoProps {
  className?: string
  href?: string
  showImage?: boolean
  size?: "sm" | "md" | "lg"
}

export function Logo({ className, href, showImage = true, size = "md" }: LogoProps) {
  const sizeClasses = {
    sm: "text-xl",
    md: "text-2xl",
    lg: "text-3xl"
  }

  const imageSizes = {
    sm: { width: 32, height: 32 },
    md: { width: 36, height: 36 },
    lg: { width: 44, height: 44 }
  }

  const logoContent = (
    <div className={cn("flex items-center", className)}>
      {showImage && (
        <div className="relative mr-2 flex items-center" style={imageSizes[size]}>
          <Image
            src="/Frameio Logo Png.png"
            alt="Frameio Logo"
            width={imageSizes[size].width}
            height={imageSizes[size].height}
            className="object-contain"
            priority
          />
        </div>
      )}
      <span className={cn("font-bold", sizeClasses[size])}>
        <span className="text-[#1B2951]">Frame</span>
        <span className="text-[#8B2635]">io</span>
      </span>
    </div>
  )

  if (href) {
    return (
      <Link href={href} className="flex items-center">
        {logoContent}
      </Link>
    )
  }

  return logoContent
}

