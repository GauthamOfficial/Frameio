"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Facebook, Instagram, Mail, Phone, Sparkles, Palette, Zap, Target } from "lucide-react"
import { Footer } from "@/components/layout/footer"
import Link from "next/link"

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background fabric-texture">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">F</span>
              </div>
              <span className="text-xl font-bold text-foreground">Frameio</span>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link
                href="/"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Home
              </Link>
              <Link
                href="/about"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="text-sm font-medium text-[#8B2635] hover:text-[#8B2635]/80 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-[#8B2635]/10"
              >
                Contact Us
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto space-y-16">
          {/* Page Title */}
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              About Frameio
            </h1>
            <p className="text-xl text-muted-foreground">
              Empowering textile businesses with AI-driven design innovation
            </p>
          </div>

          {/* Company Vision */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                  <Target className="h-6 w-6 text-primary-foreground" />
                </div>
                <CardTitle className="text-2xl">Company Vision</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-foreground leading-relaxed">
                Frameio's vision is to empower every textile business with intelligent, AI-driven design tools that simplify content creation, boost brand visibility, and help businesses grow through creativity and innovation.
              </p>
            </CardContent>
          </Card>

          {/* Company Mission */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-accent rounded-lg flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-accent-foreground" />
                </div>
                <CardTitle className="text-2xl">Company Mission</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-foreground leading-relaxed">
                Our mission is to make high-quality poster design accessible to all textile companies by combining advanced AI, seamless user experience, and smart automation-enabling brands to generate stunning visuals in seconds.
              </p>
            </CardContent>
          </Card>

          {/* Highlights Section */}
          <div>
            <h2 className="text-3xl font-bold text-foreground mb-8 text-center">
              What We Offer
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="textile-hover textile-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-chart-1 rounded-lg mb-4 flex items-center justify-center">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>AI-Powered Poster Creation</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Leverage cutting-edge artificial intelligence to generate professional, brand-aligned posters in seconds. Our AI understands your brand identity and creates designs that resonate with your audience.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="textile-hover textile-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-chart-2 rounded-lg mb-4 flex items-center justify-center">
                    <Palette className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>Textile-Ready Design Templates</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Access a comprehensive library of templates specifically designed for textile businesses. From seasonal collections to promotional campaigns, find the perfect design for every occasion.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="textile-hover textile-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-chart-3 rounded-lg mb-4 flex items-center justify-center">
                    <Target className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>Smart Brand Identity Integration</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Seamlessly integrate your brand colors, logos, and style guidelines. Our platform automatically applies your brand identity to every design, ensuring consistent visual communication.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="textile-hover textile-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-chart-4 rounded-lg mb-4 flex items-center justify-center">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>Fast, High-Quality Visual Output</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    Generate publication-ready designs instantly without compromising on quality. Export in multiple formats optimized for social media, print, and digital marketing channels.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Social Media Section */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl text-center">Connect With Us</CardTitle>
              <CardDescription className="text-center">
                Follow us on social media and stay updated with the latest features and updates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap justify-center gap-6">
                <a
                  href="https://www.facebook.com/share/1FfjVzCy2m/?mibextid=wwXIfr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-lg border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 hover:scale-105"
                >
                  <Facebook className="h-6 w-6 text-primary" />
                  <span className="font-medium">Facebook</span>
                </a>

                <a
                  href="https://www.instagram.com/frameioai?igsh=NDh6OW03NG51MDR3"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-lg border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 hover:scale-105"
                >
                  <Instagram className="h-6 w-6 text-primary" />
                  <span className="font-medium">Instagram</span>
                </a>

                <a
                  href="mailto:startuptsg@gmail.com"
                  className="flex items-center gap-3 p-4 rounded-lg border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 hover:scale-105"
                >
                  <Mail className="h-6 w-6 text-primary" />
                  <span className="font-medium">Email</span>
                </a>

                <a
                  href="tel:0759819250"
                  className="flex items-center gap-3 p-4 rounded-lg border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 hover:scale-105"
                >
                  <Phone className="h-6 w-6 text-primary" />
                  <span className="font-medium">Phone</span>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

