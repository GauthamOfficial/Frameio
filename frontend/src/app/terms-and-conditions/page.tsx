"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Footer } from "@/components/layout/footer"
import { Logo } from "@/components/common/logo"
import Link from "next/link"

export default function TermsAndConditionsPage() {
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
              Terms of Service for Frameio
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
                By using the Frameio service, you agree to be bound by the following terms and conditions. If you do not agree to these terms, please do not use the Service.
              </p>
            </CardContent>
          </Card>

          {/* Description of Service */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">1. Description of Service</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                Frameio is a Software as a Service (SaaS) platform that provides AI-powered design generation services, including the creation of posters, catalogs, logos, and other marketing materials using artificial intelligence.
              </p>
            </CardContent>
          </Card>

          {/* Errors and Inaccuracies */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">2. Errors and Inaccuracies</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                While we strive to provide accurate and high-quality AI-generated designs, the Service relies on artificial intelligence which may produce errors, inaccuracies, or results that do not meet your expectations. You acknowledge that:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>AI-generated designs should be reviewed before use</li>
                <li>Frameio is not liable for decisions made based on AI-generated content</li>
                <li>Design quality may vary and may require manual adjustments</li>
                <li>We do not guarantee that generated designs will be suitable for your specific use case</li>
              </ul>
            </CardContent>
          </Card>

          {/* Use of Data */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">3. Use of Data</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                By using the Service, you consent to Frameio collecting and using the data you provide, including design prompts, generated designs, and usage patterns, to enhance the Service and improve our AI algorithms. Your data may be anonymized and used for research and development purposes. We do not sell your personally identifiable information to third parties.
              </p>
            </CardContent>
          </Card>

          {/* Payment Terms */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">4. Payment Terms</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                When subscribing to the Service, you agree to pay the fees as outlined in your subscription plan. Failure to make payments may result in suspension or termination of access to the Service. Payments are processed through Stripe and are non-refundable, with no refunds or credits for partially used subscription periods unless otherwise stated.
              </p>
            </CardContent>
          </Card>

          {/* Intellectual Property */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">5. Intellectual Property</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Your Content:</strong> You retain ownership of designs you create using the Service</li>
                <li><strong>Service Content:</strong> Frameio retains all rights to the Service, including its technology, software, and proprietary algorithms</li>
                <li><strong>AI-Generated Content:</strong> Designs generated by our AI service are provided for your use, subject to these Terms</li>
              </ul>
            </CardContent>
          </Card>

          {/* User Responsibilities */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">6. User Responsibilities</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                You agree to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Use the Service only for lawful purposes</li>
                <li>Not upload or generate content that is illegal, harmful, or violates third-party rights</li>
                <li>Maintain the security of your account credentials</li>
                <li>Be responsible for all activities under your account</li>
              </ul>
            </CardContent>
          </Card>

          {/* Changes to the Terms */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">7. Changes to the Terms</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                Frameio reserves the right to update or modify these Terms of Service at any time without prior notice. Continued use of the Service after such changes constitutes your acceptance of the new terms.
              </p>
            </CardContent>
          </Card>

          {/* Termination */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">8. Termination</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                Frameio reserves the right to terminate or suspend access to the Service at any time, with or without cause, and with or without notice, particularly in cases of violation of these Terms or payment failure.
              </p>
            </CardContent>
          </Card>

          {/* Limitation of Liability */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">9. Limitation of Liability</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                Frameio shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the Service, including but not limited to loss of data, business interruption, or loss of profits.
              </p>
            </CardContent>
          </Card>

          {/* Governing Law */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">10. Governing Law</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                These Terms of Service are governed by the laws of [Your Jurisdiction], without regard to its conflict of law principles.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

