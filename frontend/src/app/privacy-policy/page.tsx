"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Footer } from "@/components/layout/footer"
import { Logo } from "@/components/common/logo"
import Link from "next/link"

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-background fabric-texture">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Logo href="/" />

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
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Page Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Privacy Policy for Frameio
            </h1>
            <p className="text-lg text-muted-foreground">
              Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          {/* Introduction */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Introduction</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                At Frameio, we respect your personal data. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website and use our AI-powered design generation platform.
              </p>
              <p className="text-foreground leading-relaxed mt-4">
                By using Frameio, you agree to the practices described in this Privacy Policy. If you do not agree, please do not access or use our service.
              </p>
            </CardContent>
          </Card>

          {/* Personal Data We Collect */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">1. Personal Data We Collect</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We collect the following information:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Account Information:</strong> Full name, email address, phone number, profile picture, bio, location, website</li>
                <li><strong>Company Information:</strong> Company name, logo, contact details (WhatsApp, email, Facebook), address, brand colors and preferences</li>
                <li><strong>Design Data:</strong> AI-generated designs (posters, catalogs, logos), design prompts, templates, and related metadata</li>
                <li><strong>Usage Data:</strong> IP addresses, browser type, device information, activity logs, and analytics data</li>
                <li><strong>Authentication Data:</strong> Managed through JWT authentication service</li>
              </ul>
            </CardContent>
          </Card>

          {/* How We Use Your Information */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">2. How We Use Your Information</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We use your information to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Provide and improve our AI design generation services</li>
                <li>Process your design generation requests</li>
                <li>Store and manage your generated designs</li>
                <li>Respond to your inquiries and provide customer support</li>
                <li>Enforce our terms and conditions</li>
                <li>Analyze usage patterns to improve our platform</li>
              </ul>
            </CardContent>
          </Card>

          {/* How We Protect Your Information */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">3. How We Protect Your Information</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                Your data is stored on secure servers with encryption. We use industry-standard security measures, but no internet transmission is 100% secure. We cannot guarantee absolute security.
              </p>
            </CardContent>
          </Card>

          {/* Sharing Your Personal Data */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">4. Sharing Your Personal Data</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We may share your information with:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Service Providers:</strong> Cloudinary (image storage), Google Gemini AI (design generation), JWT (authentication), and other necessary service providers</li>
                <li><strong>Business Transfers:</strong> In case of mergers, acquisitions, or business transitions</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                We do not sell your personal information to third parties.
              </p>
            </CardContent>
          </Card>

          {/* Data Storage */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">5. Data Storage</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Database:</strong> User data and design metadata are stored in MySQL databases</li>
                <li><strong>Images:</strong> AI-generated designs are stored on Cloudinary cloud storage</li>
                <li><strong>Authentication:</strong> User authentication is managed by JWT</li>
              </ul>
            </CardContent>
          </Card>

          {/* Cookies */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">6. Cookies</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                We use cookies for authentication and analytics. You can manage cookies through your browser settings.
              </p>
            </CardContent>
          </Card>

          {/* Changes To This Privacy Policy */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">7. Changes To This Privacy Policy</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated &quot;Last updated&quot; date.
              </p>
            </CardContent>
          </Card>

          {/* Contact Us */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">8. Contact Us</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                If you have questions about this Privacy Policy, contact us through our website or support channels.
              </p>
              <div className="space-y-2 text-foreground mt-4">
                <p><strong>Email:</strong> <a href="mailto:startuptsg@gmail.com" className="text-[#8B2635] hover:underline">startuptsg@gmail.com</a></p>
                <p><strong>Phone:</strong> <a href="tel:0759819250" className="text-[#8B2635] hover:underline">0759819250</a></p>
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

