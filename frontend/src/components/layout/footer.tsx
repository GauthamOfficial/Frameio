import { cn } from "@/lib/utils"
import { Facebook, Instagram, Mail, Phone } from "lucide-react"
import Link from "next/link"

interface FooterProps {
  className?: string
}

export function Footer({ className }: FooterProps) {

  return (
    <footer className={cn("border-t border-border bg-background", className)}>
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12">
          {/* CONTACT Section */}
          <div className="flex flex-col space-y-4">
            <h4 className="font-bold text-foreground text-base uppercase tracking-wide">CONTACT</h4>
            <div className="flex flex-col space-y-2 text-sm text-muted-foreground">
              <a
                href="mailto:startuptsg@gmail.com"
                className="flex items-center gap-2 hover:text-foreground transition-colors"
              >
                <Mail className="h-4 w-4 flex-shrink-0" />
                <span>startuptsg@gmail.com</span>
              </a>
              <a
                href="tel:0759819250"
                className="flex items-center gap-2 hover:text-foreground transition-colors"
              >
                <Phone className="h-4 w-4 flex-shrink-0" />
                <span>0759819250</span>
              </a>
            </div>
          </div>

          {/* MENU Section */}
          <div className="flex flex-col space-y-4">
            <h4 className="font-bold text-foreground text-base uppercase tracking-wide">MENU</h4>
            <nav className="flex flex-col space-y-2">
              <Link
                href="/"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                Home
              </Link>
              <Link
                href="/about"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                Contact
              </Link>
            </nav>
          </div>

          {/* PRODUCTS Section */}
          <div className="flex flex-col space-y-4">
            <h4 className="font-bold text-foreground text-base uppercase tracking-wide">PRODUCTS</h4>
            <nav className="flex flex-col space-y-2">
              <Link
                href="/dashboard/poster-generator"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                AI Poster Generator
              </Link>
              <Link
                href="/dashboard/branding-kit"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                Branding Kit
              </Link>
              <Link
                href="/dashboard/templates"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors underline underline-offset-4"
              >
                Templates
              </Link>
            </nav>
          </div>

          {/* FOLLOW US Section */}
          <div className="flex flex-col space-y-4">
            <h4 className="font-bold text-foreground text-base uppercase tracking-wide">FOLLOW US</h4>
            <div className="flex gap-3">
              <a
                href="https://www.facebook.com/share/1FfjVzCy2m/?mibextid=wwXIfr"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center hover:bg-accent hover:text-accent-foreground transition-all duration-200"
                aria-label="Facebook"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a
                href="https://www.instagram.com/frameioai?igsh=NDh6OW03NG51MDR3"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center hover:bg-accent hover:text-accent-foreground transition-all duration-200"
                aria-label="Instagram"
              >
                <Instagram className="h-5 w-5" />
              </a>
              <a
                href="mailto:startuptsg@gmail.com"
                className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center hover:bg-accent hover:text-accent-foreground transition-all duration-200"
                aria-label="Email"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

        </div>

        <div className="border-t border-border mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-center items-center">
            <p className="text-sm text-muted-foreground">
              <span className="font-bold text-foreground">Frameio</span> © 2025 Frameio. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
