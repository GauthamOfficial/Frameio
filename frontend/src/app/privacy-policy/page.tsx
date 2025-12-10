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
              Privacy Policy
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
                Welcome to Frameio. We are committed to protecting your privacy and ensuring you have a positive experience on our platform. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered poster generation service.
              </p>
              <p className="text-foreground leading-relaxed mt-4">
                By using Frameio, you agree to the collection and use of information in accordance with this policy. If you do not agree with our policies and practices, please do not use our service.
              </p>
            </CardContent>
          </Card>

          {/* Information We Collect */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Information We Collect</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <h3 className="text-lg font-semibold text-foreground mb-3">Personal Information</h3>
              <p className="text-foreground leading-relaxed mb-4">
                We collect information that you provide directly to us, including:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Name and contact information (email address, phone number)</li>
                <li>Account credentials (username, password)</li>
                <li>Payment information (processed securely through third-party payment processors)</li>
                <li>Brand identity information (logos, color schemes, design preferences)</li>
                <li>Content you create or upload (poster designs, images, text)</li>
              </ul>

              <h3 className="text-lg font-semibold text-foreground mb-3 mt-6">Automatically Collected Information</h3>
              <p className="text-foreground leading-relaxed mb-4">
                When you access our service, we automatically collect certain information:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Device information (IP address, browser type, operating system)</li>
                <li>Usage data (pages visited, features used, time spent on platform)</li>
                <li>Cookies and similar tracking technologies</li>
                <li>Log files and analytics data</li>
              </ul>
            </CardContent>
          </Card>

          {/* How We Use Information */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">How We Use Information</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We use the collected information for various purposes:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>To provide, maintain, and improve our AI poster generation service</li>
                <li>To process transactions and manage your account</li>
                <li>To personalize your experience and deliver content relevant to your brand</li>
                <li>To communicate with you about your account, updates, and promotional offers</li>
                <li>To analyze usage patterns and optimize our platform performance</li>
                <li>To detect, prevent, and address technical issues and security threats</li>
                <li>To comply with legal obligations and enforce our terms of service</li>
              </ul>
            </CardContent>
          </Card>

          {/* Data Storage & Security */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Data Storage & Security</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We implement industry-standard security measures to protect your information:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Encryption of data in transit and at rest</li>
                <li>Secure authentication and access controls</li>
                <li>Regular security audits and vulnerability assessments</li>
                <li>Limited access to personal information on a need-to-know basis</li>
                <li>Secure cloud storage infrastructure with reputable providers</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your information, we cannot guarantee absolute security.
              </p>
            </CardContent>
          </Card>

          {/* Third-party Services */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Third-party Services</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We may use third-party services that collect, monitor, and analyze information to help us operate our platform. These services include:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li>Payment processors for transaction handling</li>
                <li>Cloud hosting providers for data storage</li>
                <li>Analytics services to understand user behavior</li>
                <li>AI service providers for poster generation features</li>
                <li>Email service providers for communications</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                These third parties have access to your information only to perform specific tasks on our behalf and are obligated not to disclose or use it for any other purpose.
              </p>
            </CardContent>
          </Card>

          {/* User Rights */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">User Rights</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                You have the following rights regarding your personal information:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Access:</strong> Request a copy of the personal information we hold about you</li>
                <li><strong>Correction:</strong> Request correction of inaccurate or incomplete information</li>
                <li><strong>Deletion:</strong> Request deletion of your personal information, subject to legal requirements</li>
                <li><strong>Portability:</strong> Request transfer of your data to another service provider</li>
                <li><strong>Objection:</strong> Object to processing of your information for certain purposes</li>
                <li><strong>Withdrawal:</strong> Withdraw consent where processing is based on consent</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                To exercise these rights, please contact us using the information provided in the Contact Information section below.
              </p>
            </CardContent>
          </Card>

          {/* Cookies */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Cookies</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We use cookies and similar tracking technologies to track activity on our platform and store certain information. Cookies are files with a small amount of data that may include an anonymous unique identifier.
              </p>
              <p className="text-foreground leading-relaxed mb-4">
                Types of cookies we use:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-foreground">
                <li><strong>Essential Cookies:</strong> Required for the platform to function properly</li>
                <li><strong>Analytics Cookies:</strong> Help us understand how visitors interact with our platform</li>
                <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
                <li><strong>Marketing Cookies:</strong> Used to deliver relevant advertisements</li>
              </ul>
              <p className="text-foreground leading-relaxed mt-4">
                You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, if you do not accept cookies, you may not be able to use some portions of our service.
              </p>
            </CardContent>
          </Card>

          {/* Changes to Policy */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Changes to Policy</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date. You are advised to review this Privacy Policy periodically for any changes. Changes to this Privacy Policy are effective when they are posted on this page.
              </p>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-slate max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                If you have any questions about this Privacy Policy or wish to exercise your rights, please contact us:
              </p>
              <div className="space-y-2 text-foreground">
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

